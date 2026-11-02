"""Chapter 5: a dbt project as Dagster assets and checks.

Run from any folder (it writes only to a temporary directory):
    uv run --with dagster-dbt --with dbt-duckdb python 05_dagster_dbt.py
"""
import os, tempfile
os.chdir(tempfile.mkdtemp())

# --- dagster_dbt ---
import pathlib
import dagster as dg
from dagster_dbt import DbtCliResource, DbtProject, dbt_assets
root = pathlib.Path("taxi_dbt"); (root / "models").mkdir(parents=True)
(root / "dbt_project.yml").write_text("name: taxi\nprofile: taxi\nmodel-paths: [models]\n")
(root / "profiles.yml").write_text("taxi:\n  target: dev\n  outputs:\n    dev: {type: duckdb, path: warehouse.duckdb}\n")
(root / "models/stg_trips.sql").write_text("select 1 as trip_id, 12.5 as fare union all select 2, 8.0")
(root / "models/zone_mart.sql").write_text("select count(*) as trips, sum(fare) as fares from {{ ref('stg_trips') }}")
(root / "models/schema.yml").write_text("""version: 2
models:
  - name: stg_trips
    columns:
      - name: trip_id
        data_tests: [unique, not_null]
""")
project = DbtProject(project_dir=root, profiles_dir=root)
project.preparer.prepare(project)                # writes target/manifest.json

@dbt_assets(manifest=project.manifest_path)
def taxi_models(context: dg.AssetExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context=context).stream()

result = dg.materialize([taxi_models], resources={"dbt": DbtCliResource(project_dir=project)})
print("success:", result.success)
print("assets:", sorted(m.asset_key.to_user_string() for m in result.asset_materializations_for_node(taxi_models.op.name)))
print("checks:", sorted(c.check_name for c in result.get_asset_check_evaluations()))
print("--- dagster_dbt done")
