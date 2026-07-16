"""
Script de prueba comparativa: Gemini API vs Vertex AI
Permite probar ambos evaluadores con el mismo caso de prueba
"""

import os
import sys
from evaluator_factory import create_evaluator
from ai_evaluator import evaluation_to_dict

# Datos de prueba
TEST_QUESTION = "¿Cuáles son los montos de inembargabilidad?"
TEST_SOURCES = """
Montos de Inembargabilidad - Davivienda 2025

Proceso Judicial:
- Monto inembargable: $52,385,727
- Aplica para procesos judiciales ordinarios
- Base legal: Código General del Proceso

Proceso Coactivo:
- Monto inembargable: $35,587,500
- Aplica para cobro coactivo de entidades públicas
- Base legal: Estatuto Tributario

Notas:
- Estos montos se actualizan anualmente según SMMLV
- El embargo solo aplica sobre valores que excedan estos montos
"""

TEST_RESPONSE = """
Los montos de inembargabilidad en Davivienda para 2025 son:

**Proceso Judicial:** $52,385,727
**Proceso Coactivo:** $35,587,500

Estos montos protegen tus recursos hasta ese límite, dependiendo del tipo de proceso.
Los valores se actualizan anualmente según el salario mínimo legal vigente.
"""


def test_evaluator(evaluator_name: str, evaluator):
    """Prueba un evaluador con el caso de prueba"""

    print(f"\n{'='*70}")
    print(f"🧪 PROBANDO: {evaluator_name}")
    print(f"{'='*70}\n")

    try:
        evaluation = evaluator.evaluate(
            user_question=TEST_QUESTION,
            sources=TEST_SOURCES,
            ai_response=TEST_RESPONSE,
            trace_id=f"test-{evaluator_name.lower()}",
            session_id="comparison-test"
        )

        # Mostrar resultados
        print(f"✅ Evaluación completada exitosamente!\n")

        print(f"📝 Question Quality:")
        print(f"   Clarity: {evaluation.question_quality.clarity_score}/5")
        print(f"   Ambiguous: {evaluation.question_quality.is_ambiguous}")

        print(f"\n🔍 Hallucination Check:")
        print(f"   Detected: {evaluation.hallucination_check.detected}")
        print(f"   Severity: {evaluation.hallucination_check.severity}")

        print(f"\n⚖️  Quality Scores:")
        print(f"   Fidelity:     {evaluation.fidelity_score.score}/5")
        print(f"   Completeness: {evaluation.completeness.score}/5")
        print(f"   Relevance:    {evaluation.relevance.score}/5")
        print(f"   Coherence:    {evaluation.coherence.score}/5")

        print(f"\n📊 Overall Assessment:")
        print(f"   Overall Score:  {evaluation.overall_quality.overall_score:.2f}/5.0")
        print(f"   Quality Tier:   {evaluation.overall_quality.quality_tier}")
        print(f"   Recommendation: {evaluation.overall_quality.recommendation}")
        print(f"   Acceptable:     {evaluation.overall_quality.acceptable}")

        if evaluation.verification_applied:
            print(f"\n⚠️  Verification: Applied")

        return evaluation

    except Exception as e:
        print(f"❌ Error durante evaluación: {e}")
        import traceback
        traceback.print_exc()
        return None


def compare_evaluators():
    """Ejecuta comparación entre ambos evaluadores"""

    print("\n" + "="*70)
    print("🔬 COMPARACIÓN DE EVALUADORES: GEMINI API vs VERTEX AI")
    print("="*70)

    print("\n📋 Caso de Prueba:")
    print(f"   Pregunta: {TEST_QUESTION}")
    print(f"   Fuentes: {len(TEST_SOURCES)} caracteres")
    print(f"   Respuesta: {len(TEST_RESPONSE)} caracteres")

    results = {}

    # ──────────────────────────────────────────────────────────────────
    # PROBAR GEMINI API
    # ──────────────────────────────────────────────────────────────────

    gemini_api_key = os.getenv('GEMINI_API_KEY')

    if gemini_api_key:
        try:
            evaluator_gemini = create_evaluator(
                evaluator_type="gemini",
                gemini_api_key=gemini_api_key
            )
            results['gemini'] = test_evaluator("GEMINI API", evaluator_gemini)
        except Exception as e:
            print(f"\n⚠️  No se pudo probar Gemini API: {e}")
            results['gemini'] = None
    else:
        print(f"\n⚠️  GEMINI_API_KEY no configurado - omitiendo Gemini API")
        results['gemini'] = None

    # ──────────────────────────────────────────────────────────────────
    # PROBAR VERTEX AI
    # ──────────────────────────────────────────────────────────────────

    gcp_project_id = os.getenv('GCP_PROJECT_ID')

    if gcp_project_id:
        try:
            evaluator_vertex = create_evaluator(
                evaluator_type="vertex",
                gcp_project_id=gcp_project_id,
                gcp_location=os.getenv('GCP_LOCATION', 'us-central1'),
                service_account_key_path=os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            )
            results['vertex'] = test_evaluator("VERTEX AI", evaluator_vertex)
        except Exception as e:
            print(f"\n⚠️  No se pudo probar Vertex AI: {e}")
            results['vertex'] = None
    else:
        print(f"\n⚠️  GCP_PROJECT_ID no configurado - omitiendo Vertex AI")
        results['vertex'] = None

    # ──────────────────────────────────────────────────────────────────
    # COMPARACIÓN DE RESULTADOS
    # ──────────────────────────────────────────────────────────────────

    if results['gemini'] and results['vertex']:
        print(f"\n{'='*70}")
        print("📊 COMPARACIÓN DE RESULTADOS")
        print(f"{'='*70}\n")

        print(f"{'Métrica':<25} {'Gemini API':<20} {'Vertex AI':<20}")
        print(f"{'-'*70}")

        # Question Quality
        print(f"{'Question Clarity':<25} "
              f"{results['gemini'].question_quality.clarity_score:<20} "
              f"{results['vertex'].question_quality.clarity_score:<20}")

        # Hallucination
        print(f"{'Hallucination Detected':<25} "
              f"{str(results['gemini'].hallucination_check.detected):<20} "
              f"{str(results['vertex'].hallucination_check.detected):<20}")

        # Scores
        print(f"{'Fidelity Score':<25} "
              f"{results['gemini'].fidelity_score.score:<20} "
              f"{results['vertex'].fidelity_score.score:<20}")

        print(f"{'Completeness Score':<25} "
              f"{results['gemini'].completeness.score:<20} "
              f"{results['vertex'].completeness.score:<20}")

        print(f"{'Relevance Score':<25} "
              f"{results['gemini'].relevance.score:<20} "
              f"{results['vertex'].relevance.score:<20}")

        print(f"{'Coherence Score':<25} "
              f"{results['gemini'].coherence.score:<20} "
              f"{results['vertex'].coherence.score:<20}")

        # Overall
        print(f"{'-'*70}")
        print(f"{'Overall Score':<25} "
              f"{results['gemini'].overall_quality.overall_score:<20.2f} "
              f"{results['vertex'].overall_quality.overall_score:<20.2f}")

        print(f"{'Quality Tier':<25} "
              f"{results['gemini'].overall_quality.quality_tier:<20} "
              f"{results['vertex'].overall_quality.quality_tier:<20}")

        print(f"{'Recommendation':<25} "
              f"{results['gemini'].overall_quality.recommendation:<20} "
              f"{results['vertex'].overall_quality.recommendation:<20}")

        # Análisis de diferencias
        score_diff = abs(
            results['gemini'].overall_quality.overall_score -
            results['vertex'].overall_quality.overall_score
        )

        print(f"\n{'='*70}")
        print("📈 ANÁLISIS")
        print(f"{'='*70}\n")

        print(f"Diferencia en Overall Score: {score_diff:.2f}")

        if score_diff < 0.1:
            print("✅ Resultados prácticamente idénticos")
        elif score_diff < 0.5:
            print("⚠️  Diferencias menores (esperado por variabilidad del modelo)")
        else:
            print("🔴 Diferencias significativas - revisar configuración")

        print("\n💡 Conclusión:")
        print("   Ambos evaluadores usan el mismo modelo (gemini-2.0-flash)")
        print("   y los mismos prompts, por lo que los resultados deberían")
        print("   ser muy similares. Diferencias menores son esperadas por")
        print("   la naturaleza estocástica de los LLMs.\n")

    elif not results['gemini'] and not results['vertex']:
        print(f"\n❌ No se pudieron probar ninguno de los evaluadores")
        print(f"\nConfigura al menos uno:")
        print(f"  - Gemini API:  export GEMINI_API_KEY='your-key'")
        print(f"  - Vertex AI:   export GCP_PROJECT_ID='your-project'")

    else:
        print(f"\n⚠️  Solo se probó un evaluador")
        print(f"   Gemini API: {'✅' if results['gemini'] else '❌'}")
        print(f"   Vertex AI:  {'✅' if results['vertex'] else '❌'}")

    # ──────────────────────────────────────────────────────────────────
    # RECOMENDACIÓN
    # ──────────────────────────────────────────────────────────────────

    print(f"\n{'='*70}")
    print("🎯 RECOMENDACIÓN DE USO")
    print(f"{'='*70}\n")

    print("📍 Gemini API Directa:")
    print("   ✅ Desarrollo local y prototipado")
    print("   ✅ Setup más simple")
    print("   ⚠️  Cuotas limitadas (1,500 RPD free, 2,000 RPM paid)")
    print("   ⚠️  Seguridad básica (API key)")

    print("\n☁️  Vertex AI:")
    print("   ✅ Producción y entornos empresariales")
    print("   ✅ Cuotas mucho más altas")
    print("   ✅ Seguridad enterprise (IAM, logging, monitoring)")
    print("   ✅ Auditoría completa en Cloud Console")
    print("   ⚠️  Requiere configuración GCP")

    print(f"\n{'='*70}\n")


if __name__ == "__main__":
    try:
        compare_evaluators()
    except KeyboardInterrupt:
        print("\n\n⚠️  Prueba interrumpida por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error durante la comparación: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
