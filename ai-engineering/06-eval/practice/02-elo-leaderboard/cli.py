#!/usr/bin/env python3
"""
Experiment 6-6: build a model leaderboard from pairwise comparisons — command-line entry point

A single argparse CLI that splits the pipeline into subcommands:

    battle        run pairwise battles and write results (simulated / real Chatbot Arena data / LLM judge)
    elo           compute Elo or Bradley-Terry ratings from battle results
    leaderboard   render battle results or ratings as the final leaderboard table
    pipeline      run battle -> Elo -> leaderboard in one step (offline and reproducible by default)

The simulate/arena battle sources and elo, leaderboard and pipeline are fully offline
and need no API. Only --source llm (LLM-judged battles) needs an API key: it prefers
Anthropic (ANTHROPIC_API_KEY) and falls back to OpenRouter (OPENROUTER_API_KEY);
--judge-backend openrouter forces OpenRouter (e.g. when the direct key is invalid).

Examples:
    # Offline end to end: simulated battles -> Elo -> leaderboard
    python cli.py pipeline

    # Step by step
    python cli.py battle --source simulate --num-battles 5000 --output battles.json
    python cli.py elo --input battles.json --method bradley-terry --bootstrap 100
    python cli.py leaderboard --input battles.json --top-n 20
"""
import argparse
import json
import os
import sys
import warnings
from typing import List, Optional

import pandas as pd

# Newer sklearn raises a FutureWarning for LogisticRegression(penalty=None) in
# Bradley-Terry; bootstrap repeats it hundreds of times, so silence it to keep output clean.
warnings.filterwarnings("ignore", category=FutureWarning, module="sklearn")

from battle_simulator import DEFAULT_TRUE_SKILLS, simulate_battles
from elo_rating import EloRatingSystem


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _load_battles(path: str) -> pd.DataFrame:
    """Load battle results from JSON as a DataFrame with model_a/model_b/winner columns."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    # `[]` from --num-battles 0 has no columns; treat as empty battle frame.
    if len(df) == 0:
        return pd.DataFrame(columns=["model_a", "model_b", "winner"])
    required = {"model_a", "model_b", "winner"}
    if not required.issubset(df.columns):
        raise ValueError(
            f"Battle file {path} is missing required fields {required}; found: {list(df.columns)}"
        )
    return df


def _save_json(obj, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def _battle_stats(df: pd.DataFrame) -> dict:
    """Count battles and wins per model (a tie counts as 0.5)."""
    matches: dict = {}
    wins: dict = {}
    for model_a, model_b, winner in zip(df["model_a"], df["model_b"], df["winner"]):
        matches[model_a] = matches.get(model_a, 0) + 1
        matches[model_b] = matches.get(model_b, 0) + 1
        if winner == "model_a":
            wins[model_a] = wins.get(model_a, 0) + 1.0
        elif winner == "model_b":
            wins[model_b] = wins.get(model_b, 0) + 1.0
        else:  # tie / tie (bothbad)
            wins[model_a] = wins.get(model_a, 0) + 0.5
            wins[model_b] = wins.get(model_b, 0) + 0.5
    return {"matches": matches, "wins": wins}


def _compute_online_elo(df: pd.DataFrame, k: float, init_rating: float) -> pd.DataFrame:
    """Online incremental Elo (records in order); returns a DataFrame with model/rating columns."""
    elo = EloRatingSystem(initial_rating=init_rating, k_factor=k)
    for model_a, model_b, winner in zip(df["model_a"], df["model_b"], df["winner"]):
        elo.update_ratings(model_a, model_b, winner)
    rows = [(m, r) for m, r, *_ in elo.get_leaderboard()]
    return pd.DataFrame(rows, columns=["model", "rating"])


def _compute_bradley_terry(df: pd.DataFrame, bootstrap: int) -> pd.DataFrame:
    """Bradley-Terry MLE ratings (optional bootstrap confidence intervals)."""
    # Lazy import: Bradley-Terry needs scikit-learn, so load it only when used.
    from bradley_terry import compute_bradley_terry_leaderboard
    return compute_bradley_terry_leaderboard(df, bootstrap_rounds=bootstrap)


def _compute_ratings(df: pd.DataFrame, method: str, k: float,
                     init_rating: float, bootstrap: int) -> pd.DataFrame:
    if method == "bradley-terry":
        return _compute_bradley_terry(df, bootstrap)
    return _compute_online_elo(df, k, init_rating)


def _print_leaderboard(ratings: pd.DataFrame, df: Optional[pd.DataFrame],
                       top_n: int, title: str) -> None:
    """Print the leaderboard table, with a 95% CI column if the ratings have intervals."""
    has_ci = {"lower_ci", "upper_ci"}.issubset(ratings.columns)
    stats = _battle_stats(df) if df is not None else {"matches": {}, "wins": {}}

    ratings = ratings.sort_values("rating", ascending=False).reset_index(drop=True)

    print("=" * 78)
    print(title)
    print("=" * 78)
    if has_ci:
        header = f"{'Rank':<6}{'Model':<24}{'Elo':>8}   {'95% CI':<20}{'Games':>7}{'Win %':>9}"
    else:
        header = f"{'Rank':<6}{'Model':<24}{'Elo':>8}   {'Games':>7}{'Win %':>9}"
    print(header)
    print("-" * 78)

    for idx, row in ratings.head(top_n).iterrows():
        model = str(row["model"])
        n = stats["matches"].get(model, 0)
        w = stats["wins"].get(model, 0.0)
        win_rate = (w / n * 100.0) if n else 0.0
        if has_ci:
            ci = f"[{row['lower_ci']:.0f}, {row['upper_ci']:.0f}]"
            print(f"{idx + 1:<6}{model:<24}{row['rating']:>8.1f}   "
                  f"{ci:<20}{n:>7}{win_rate:>8.1f}%")
        else:
            print(f"{idx + 1:<6}{model:<24}{row['rating']:>8.1f}   "
                  f"{n:>7}{win_rate:>8.1f}%")
    print("-" * 78)
    print(f"{len(ratings)} models, "
          f"ratings from {ratings['rating'].min():.1f} to {ratings['rating'].max():.1f}")
    if has_ci:
        avg_ci = (ratings["upper_ci"] - ratings["lower_ci"]).mean()
        print(f"Mean 95% CI width: {avg_ci:.1f} points")
    print()


# --------------------------------------------------------------------------- #
# Subcommands
# --------------------------------------------------------------------------- #
def _make_battles(args) -> List[dict]:
    if args.source == "simulate":
        skills = DEFAULT_TRUE_SKILLS
        if args.models:
            # With user-supplied model names, space latent skills evenly around 1000.
            n = len(args.models)
            skills = {m: 1000.0 + (n - 1 - 2 * i) * 40.0 for i, m in enumerate(args.models)}
        print(f"Simulating {args.num_battles} battles ({len(skills)} models, "
              f"tie probability {args.tie_prob}, seed {args.seed})...")
        battles = simulate_battles(skills, args.num_battles,
                                   tie_prob=args.tie_prob, seed=args.seed)
        print("True latent skills (for comparison afterwards):")
        for m, s in sorted(skills.items(), key=lambda kv: -kv[1]):
            print(f"  {m:<24}{s:>8.1f}")
        return battles

    if args.source == "arena":
        from data_loader import load_arena_data, filter_data
        from parallel_processing import optimize_dataframe
        if not os.path.exists(args.arena_file):
            print(f"Error: Chatbot Arena data file {args.arena_file} not found.", file=sys.stderr)
            print("Download it from the URL below and save it under that name:", file=sys.stderr)
            print("https://storage.googleapis.com/arena_external_data/public/"
                  "clean_battle_20240814_public.json", file=sys.stderr)
            sys.exit(1)
        df = load_arena_data(args.arena_file)
        df = optimize_dataframe(df)
        df = filter_data(df, anony_only=True, use_dedup=True, min_turn=1)
        if args.sample and args.sample < len(df):
            df = df.sample(n=args.sample, random_state=args.seed).reset_index(drop=True)
            print(f"Sampled {args.sample} battles.")
        return df[["model_a", "model_b", "winner"]].to_dict("records")

    # source == "llm"
    from llm_judge import run_llm_battles
    print("Running LLM-judged battles (order swapped to cancel position bias)...")
    return run_llm_battles(
        candidate_models=args.candidate_models,
        judge_model=args.judge_model,
        backend=args.judge_backend,
    )


def cmd_battle(args) -> None:
    battles = _make_battles(args)
    _save_json(battles, args.output)
    print(f"\nGenerated {len(battles)} battles, written to {args.output}")


def cmd_elo(args) -> None:
    df = _load_battles(args.input)
    print(f"Loaded {len(df)} battles from {args.input}, method: {args.method}")
    ratings = _compute_ratings(df, args.method, args.k, args.init_rating, args.bootstrap)
    _print_leaderboard(ratings, df, top_n=args.top_n,
                       title=f"Elo ratings ({args.method})")
    if args.output:
        _save_json(ratings.to_dict("records"), args.output)
        print(f"Ratings written to {args.output}")


def cmd_leaderboard(args) -> None:
    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)
    sample = data[0] if isinstance(data, list) and data else {}
    if "rating" in sample:  # Input is already a ratings file; show it directly.
        ratings = pd.DataFrame(data)
        _print_leaderboard(ratings, None, top_n=args.top_n, title="Model leaderboard")
        return
    # Otherwise treat it as a battle file: compute ratings, then show them.
    df = _load_battles(args.input)
    print(f"Loaded {len(df)} battles from {args.input}, method: {args.method}")
    ratings = _compute_ratings(df, args.method, args.k, args.init_rating, args.bootstrap)
    _print_leaderboard(ratings, df, top_n=args.top_n, title="Model leaderboard")


def cmd_pipeline(args) -> None:
    print("=" * 78)
    print("Experiment 6-6: battles -> Elo -> leaderboard (end to end)")
    print("=" * 78)
    battles = _make_battles(args)
    if args.output:
        _save_json(battles, args.output)
        print(f"Battle results written to {args.output}")
    df = pd.DataFrame(battles)
    print(f"\nComputing ratings from {len(df)} battles with {args.method}...")
    ratings = _compute_ratings(df, args.method, args.k, args.init_rating, args.bootstrap)
    _print_leaderboard(ratings, df, top_n=args.top_n, title="Final leaderboard")


# --------------------------------------------------------------------------- #
# Argument parsing
# --------------------------------------------------------------------------- #
def _add_source_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--source", choices=["simulate", "arena", "llm"],
                        default="simulate",
                        help="Battle source: simulate=offline simulation (default), arena=real Chatbot Arena data, "
                             "llm=LLM judge (needs API)")
    parser.add_argument("--models", nargs="+", default=None,
                        help="simulate: custom model names (default: the 8 built-in models)")
    parser.add_argument("--num-battles", type=int, default=3000,
                        help="simulate: number of battles (default 3000)")
    parser.add_argument("--tie-prob", type=float, default=0.1,
                        help="simulate: tie probability (default 0.1)")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed (default 42)")
    parser.add_argument("--arena-file", default="arena_data.json",
                        help="arena: path to the Chatbot Arena data file (default arena_data.json)")
    parser.add_argument("--sample", type=int, default=0,
                        help="arena: randomly sample N battles; 0 means all (default 0)")
    parser.add_argument("--candidate-models", nargs="+", default=None,
                        help="llm: candidate models (default: Claude models)")
    parser.add_argument("--judge-model", default="claude-opus-4-8",
                        help="llm: judge model (default claude-opus-4-8)")
    parser.add_argument("--judge-backend", choices=["anthropic", "openrouter", "auto"],
                        default="auto",
                        help="llm: judge backend. auto=Anthropic if ANTHROPIC_API_KEY is set, "
                             "otherwise fall back to OpenRouter (OPENROUTER_API_KEY); "
                             "openrouter=force OpenRouter (when the direct key is invalid)")


def _add_rating_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--method", choices=["online-elo", "bradley-terry"],
                        default="online-elo",
                        help="Rating method: online-elo=incremental Elo (default), "
                             "bradley-terry=MLE fit")
    parser.add_argument("--k", type=float, default=4.0,
                        help="online-elo: K-factor / learning rate (default 4.0, the Arena value)")
    parser.add_argument("--init-rating", type=float, default=1000.0,
                        help="Initial rating (default 1000)")
    parser.add_argument("--bootstrap", type=int, default=0,
                        help="bradley-terry: bootstrap rounds for 95%% CIs (default 0 = none)")
    parser.add_argument("--top-n", type=int, default=20,
                        help="Number of models to show (default 20)")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cli.py",
        description="Experiment 6-6: build a model leaderboard from pairwise comparisons (battles -> Elo -> leaderboard)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="command", metavar="{battle,elo,leaderboard,pipeline}")

    # battle
    p_battle = sub.add_parser("battle", help="Run pairwise battles and write results")
    _add_source_args(p_battle)
    p_battle.add_argument("--output", default="battles.json",
                          help="Output file for battle results (default battles.json)")
    p_battle.set_defaults(func=cmd_battle)

    # elo
    p_elo = sub.add_parser("elo", help="Compute Elo / Bradley-Terry ratings from battle results")
    p_elo.add_argument("--input", default="battles.json",
                       help="Input battle-results file (default battles.json)")
    _add_rating_args(p_elo)
    p_elo.add_argument("--output", default=None,
                       help="Write ratings to a JSON file (optional)")
    p_elo.set_defaults(func=cmd_elo)

    # leaderboard
    p_lb = sub.add_parser("leaderboard", help="Show the final leaderboard table")
    p_lb.add_argument("--input", default="battles.json",
                      help="Input battle-results or ratings file (default battles.json)")
    _add_rating_args(p_lb)
    p_lb.set_defaults(func=cmd_leaderboard)

    # pipeline
    p_pipe = sub.add_parser("pipeline", help="Run battles -> Elo -> leaderboard in one step (offline by default)")
    _add_source_args(p_pipe)
    _add_rating_args(p_pipe)
    p_pipe.add_argument("--output", default=None,
                        help="Write battle results to a JSON file (optional)")
    p_pipe.set_defaults(func=cmd_pipeline)

    return parser


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_parser()
    # With no subcommand, run the offline end-to-end demo so it works out of the box.
    args = parser.parse_args(argv if argv is not None else (sys.argv[1:] or ["pipeline"]))
    try:
        args.func(args)
    except (RuntimeError, FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:  # e.g. anthropic.AuthenticationError from an invalid ANTHROPIC_API_KEY
        print(f"Error: {type(exc).__name__}: {exc}", file=sys.stderr)
        print("(If this was the LLM-judge path, check that the provider's API key is valid.)", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
