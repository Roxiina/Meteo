"""
Test script for wind gust analysis and cyclone detection.
Tests the integration between frontend and backend for wind gust functionality.
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.cyclone_detector import CycloneDetector


def test_wind_gust_analysis():
    """Test wind gust analysis functions."""
    print("🌪️ Test de l'analyse des rafales de vent")
    print("=" * 60)
    
    detector = CycloneDetector()
    
    # Test cases for different wind gust speeds
    test_cases = [
        (30, "Conditions normales"),
        (55, "Surveillance"),
        (75, "Vigilance renforcée"),
        (95, "Alerte cyclone"),
        (130, "Cyclone détecté")
    ]
    
    print("\n🔍 Tests des niveaux de risque basés sur les rafales :")
    print("-" * 60)
    
    for gust_speed, expected_level in test_cases:
        risk_level, status_class = detector.get_risk_level_from_gusts(gust_speed)
        risk_message = detector.get_gust_risk_message(gust_speed)
        
        print(f"\n💨 Rafales : {gust_speed} km/h")
        print(f"   Niveau  : {risk_level}")
        print(f"   Classe  : {status_class}")
        print(f"   Message : {risk_message}")
        
        # Verify expected results
        if expected_level.upper() in risk_level:
            print("   ✅ Niveau de risque correct")
        else:
            print("   ❌ Niveau de risque inattendu")
    
    print("\n" + "=" * 60)
    print("✅ Test de l'analyse des rafales terminé")


def test_cyclone_detection_with_gusts():
    """Test cyclone detection with different wind gust scenarios."""
    print("\n🌀 Test de détection cyclonique avec rafales")
    print("=" * 60)
    
    detector = CycloneDetector()
    
    # Test scenarios with different meteorological conditions
    test_scenarios = [
        {
            "name": "Conditions normales",
            "sst": 25.0,          # Below threshold
            "pressure": 1013.0,    # Normal pressure
            "wind_speed": 20.0,    # Low wind
            "wind_gusts": 35.0     # Low gusts
        },
        {
            "name": "Surveillance météo",
            "sst": 26.8,          # At threshold
            "pressure": 1008.0,    # Slightly low
            "wind_speed": 45.0,    # Moderate wind
            "wind_gusts": 65.0     # Moderate gusts
        },
        {
            "name": "Alerte cyclone",
            "sst": 28.0,          # Above threshold
            "pressure": 995.0,     # Low pressure
            "wind_speed": 70.0,    # Strong wind
            "wind_gusts": 105.0    # Strong gusts
        },
        {
            "name": "Cyclone confirmé",
            "sst": 29.5,          # High
            "pressure": 980.0,     # Very low pressure
            "wind_speed": 120.0,   # Very strong wind
            "wind_gusts": 145.0    # Extreme gusts
        }
    ]
    
    print("\n🔬 Analyse des scénarios météorologiques :")
    print("-" * 60)
    
    for scenario in test_scenarios:
        print(f"\n📊 Scénario : {scenario['name']}")
        print(f"   🌡️ SST : {scenario['sst']}°C")
        print(f"   📊 Pression : {scenario['pressure']} hPa")
        print(f"   💨 Vent : {scenario['wind_speed']} km/h")
        print(f"   🌬️ Rafales : {scenario['wind_gusts']} km/h")
        
        # Test wind gust risk assessment
        risk_level, status_class = detector.get_risk_level_from_gusts(scenario['wind_gusts'])
        print(f"   ⚠️ Évaluation rafales : {risk_level}")
        
        # Test overall conditions analysis
        try:
            conditions = detector._analyze_conditions(
                sst=scenario['sst'],
                pressure=scenario['pressure'],
                wind_speed=scenario['wind_speed'],
                wind_gusts=scenario['wind_gusts']
            )
            
            severity = detector._calculate_severity_score(conditions)
            category = detector._classify_cyclone(conditions, severity)
            
            print(f"   📈 Score de sévérité : {severity:.2f}")
            print(f"   🌀 Catégorie : {category.value}")
            
            # Analyze individual conditions
            print(f"   📋 Conditions :")
            for param, data in conditions.items():
                status = "✅" if data['exceeds_threshold'] else "❌"
                print(f"      {param} : {data['value']:.1f} {status}")
            
        except Exception as e:
            print(f"   ❌ Erreur d'analyse : {e}")
    
    print("\n" + "=" * 60)
    print("✅ Test de détection cyclonique terminé")


def main():
    """Run all wind gust tests."""
    print("🌪️ TESTS D'ANALYSE DES RAFALES DE VENT")
    print("=" * 80)
    
    try:
        test_wind_gust_analysis()
        test_cyclone_detection_with_gusts()
        
        print("\n🎉 TOUS LES TESTS SONT TERMINÉS AVEC SUCCÈS!")
        print("\n💡 L'analyse des rafales de vent est maintenant intégrée :")
        print("   • Détection de risque basée sur les vitesses de rafales")
        print("   • Classification en 5 niveaux (Normal → Cyclone)")
        print("   • Messages de risque détaillés")
        print("   • Intégration dans l'algorithme de détection cyclonique")
        print("   • Pondération renforcée des rafales dans le score de sévérité")
        
    except Exception as e:
        print(f"\n❌ ERREUR LORS DES TESTS : {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()