# Neoom PV Integration

[![CI](https://github.com/Bauxi231/has_neoom_pv/actions/workflows/ci.yml/badge.svg)](https://github.com/Bauxi231/has_neoom_pv/actions/workflows/ci.yml)
[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

Eine Home Assistant Custom Integration zur Integration von Neoom BEAAM PV-Systemen über die lokale BEAAM API.

## Features

- **Config Flow**: Einfache Einrichtung über das Home Assistant UI
- **30+ Sensoren**: Alle wichtigen PV-, Batterie-, Netz- und Verbrauchsdaten
- **Energiefluss-Fraktionen**: Anteile (PV zu Verbrauch, PV zu Batterie, etc.)
- **Echtzeit-Updates**: Konfigurierbares Update-Intervall (5-300 Sekunden)
- **Statische Konfigurationswerte**: Batteriekapazität, Maximalleistungen, etc.
- **HACS-ready**: Erfüllt die Anforderungen für den Home Assistant Community Store

## Voraussetzungen

- Home Assistant 2024.1.0 oder höher
- Neoom BEAAM System mit lokaler API erreichbar
- BEAAM API Token (Bearer Token Authentication)
- Site ID der PV-Anlage

## Installation

### Über HACS (Empfohlen)

1. Öffne HACS in Home Assistant
2. Gehe zu "Integrations"
3. Klicke auf die drei Punkte (⋮) oben rechts → "Custom repositories"
4. Füge hinzu:
   - Repository: `https://github.com/Bauxi231/has_neoom_pv`
   - Category: `Integration`
5. Klicke auf "Add"
6. Suche nach "Neoom PV" und klicke auf "Download"
7. Starte Home Assistant neu

### Manuell

1. Kopiere den Ordner `custom_components/neoom_pv` in dein `/config/custom_components/` Verzeichnis
2. Starte Home Assistant neu

## Einrichtung

1. Gehe zu **Einstellungen** → **Geräte & Dienste**
2. Klicke auf **+ Integration hinzufügen**
3. Suche nach "Neoom PV"
4. Gib folgende Daten ein:
   - **BEAAM IP Address**: Die lokale IP deines BEAAM Geräts
   - **BEAAM API Token**: Dein Bearer Token aus dem Neoom Konto für die BEAAM API
   - **Site ID**: Deine Site ID aus dem Neoom Konto
5. Klicke auf "Absenden"


## Verfügbare Sensoren

### Leistung (Watt)
- PV Leistung
- Verbrauch
- Batterie Leistung
- Netzleistung
- Wallbox Leistung (falls vorhanden)
- Heizung Leistung (falls vorhanden)
- Geräte Leistung (falls vorhanden)

### Energie (Wh)
- Produzierte Energie
- Verbrauchte Energie (berechnet)
- Geladene Energie
- Entladene Energie
- Netzbezug
- Einspeisung

### Status (%)
- Batterie Ladestand (SOC)
- Autarkiegrad
- PV zu Verbrauch
- PV zu Batterie
- PV zu Netz
- Netz zu Verbrauch
- Netz zu Batterie
- Batterie zu Verbrauch
- Batterie zu Netz

### Konfiguration (statisch)
- Batteriekapazität
- Max. PV-Leistung
- Max. Batterieleistung
- Max. Einspeiseleistung
- Max. Netzanschluss


## Energy Dashboard Integration

Die Integration ist kompatibel mit dem Home Assistant Energy Dashboard:

| Dashboard-Feld | Sensor |
|----------------|--------|
| Stromproduktion | `sensor.neoom_pv_produzierte_energie` |
| Stromverbrauch | `sensor.neoom_pv_verbrauchte_energie_berechnet` |
| Ins Netz eingespeist | `sensor.neoom_pv_einspeisung` |
| Aus dem Netz bezogen | `sensor.neoom_pv_netzbezug` |
| Batterie | `sensor.neoom_pv_batterie_ladestand` |

## CI/CD Pipeline

Diese Integration verwendet GitHub Actions für automatisiertes Testing:

- **Hassfest Validation**: Prüfung auf Home Assistant Standards
- **HACS Validation**: Prüfung auf HACS-Kompatibilität
- **Linting**: flake8, black, isort
- **Syntax Check**: Python Syntax-Validierung

## Entwicklung

```bash
git clone https://github.com/Bauxi231/has_neoom_pv.git
pip install flake8 black isort
flake8 custom_components/neoom_pv
black --check custom_components/neoom_pv
isort --check-only custom_components/neoom_pv
```


## Lizenz

MIT License - siehe [LICENSE](LICENSE)

## Support

Bei Problemen oder Feature-Wünschen:
- [GitHub Issues](https://github.com/Bauxi231/has_neoom_pv/issues)
- [Neoom Developer Documentation](https://developer.neoom.com/)

---

**Hinweis**: Diese Integration ist nicht offiziell von Neoom unterstützt. Verwende sie auf eigene Verantwortung.
