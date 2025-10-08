# Installationsanleitung - Marstek Venus Home Assistant Integration

Diese Anleitung führt Sie Schritt für Schritt durch die Installation und Konfiguration der Marstek Venus Integration für Home Assistant.

## Voraussetzungen

### Hardware
- Marstek Venus C oder Venus E Energiespeichersystem
- Home Assistant Installation (Version 2023.8.0 oder höher)
- Lokales Netzwerk (LAN/WLAN)

### Vorbereitung des Marstek Geräts

1. **Gerät mit Netzwerk verbinden**
   - Öffnen Sie die Marstek APP auf Ihrem Smartphone
   - Verbinden Sie das Gerät mit Ihrem WLAN oder Ethernet-Netzwerk
   - Notieren Sie sich die IP-Adresse des Geräts

2. **Local API aktivieren**
   - Öffnen Sie die Marstek APP
   - Gehen Sie zu den Geräteeinstellungen
   - Aktivieren Sie die "Local API" Funktion
   - Setzen Sie den UDP-Port (Standard: 30000)
   - Empfohlen: Port zwischen 49152 und 65535

3. **Statische IP-Adresse empfohlen**
   - Richten Sie in Ihrem Router eine statische IP für das Marstek-Gerät ein
   - Dies verhindert Verbindungsprobleme bei IP-Änderungen

## Installation

### Option 1: Installation über HACS (empfohlen)

#### HACS installieren (falls noch nicht vorhanden)

Falls HACS noch nicht installiert ist:

1. Öffnen Sie das Home Assistant Terminal
2. Führen Sie folgenden Befehl aus:
   ```bash
   wget -O - https://get.hacs.xyz | bash -
   ```
3. Starten Sie Home Assistant neu
4. Gehen Sie zu **Einstellungen** → **Geräte & Dienste**
5. Klicken Sie auf **+ Integration hinzufügen**
6. Suchen Sie nach "HACS" und richten Sie es ein

#### Integration über HACS installieren

1. **HACS öffnen**
   - Klicken Sie in der Seitenleiste auf **HACS**

2. **Custom Repository hinzufügen**
   - Klicken Sie auf die drei Punkte (⋮) oben rechts
   - Wählen Sie **Benutzerdefinierte Repositories**
   - Repository URL eingeben: `https://github.com/YOURUSERNAME/marstek-venus-hacs`
   - Kategorie: **Integration**
   - Klicken Sie auf **Hinzufügen**

3. **Integration installieren**
   - Suchen Sie in HACS nach "Marstek Venus"
   - Klicken Sie auf **Herunterladen**
   - Wählen Sie die neueste Version
   - Klicken Sie auf **Herunterladen**

4. **Home Assistant neu starten**
   - Gehen Sie zu **Einstellungen** → **System**
   - Klicken Sie auf **Neu starten**
   - Warten Sie, bis Home Assistant vollständig neu gestartet ist

### Option 2: Manuelle Installation

1. **Dateien herunterladen**
   - Laden Sie die neueste Version von GitHub herunter
   - Entpacken Sie die Dateien

2. **Dateien kopieren**
   ```bash
   # Verbinden Sie sich per SSH mit Home Assistant
   cd /config
   
   # Erstellen Sie das Verzeichnis (falls nicht vorhanden)
   mkdir -p custom_components
   
   # Kopieren Sie die Integration
   cp -r /pfad/zum/download/custom_components/marstek_venus custom_components/
   ```

3. **Berechtigungen prüfen**
   ```bash
   chown -R homeassistant:homeassistant custom_components/marstek_venus
   chmod -R 755 custom_components/marstek_venus
   ```

4. **Home Assistant neu starten**

## Konfiguration

### Integration einrichten

1. **Integrationen aufrufen**
   - Gehen Sie zu **Einstellungen** → **Geräte & Dienste**
   - Klicken Sie auf **+ Integration hinzufügen**

2. **Marstek Venus suchen**
   - Suchen Sie nach "Marstek Venus"
   - Klicken Sie auf die Integration

3. **Verbindungsdaten eingeben**
   - **IP-Adresse**: Die IP-Adresse Ihres Marstek-Geräts (z.B. 192.168.1.100)
   - **UDP-Port**: Der in der APP konfigurierte Port (Standard: 30000)
   - **Bluetooth MAC**: Optional, für automatische Erkennung "0" eingeben

4. **Konfiguration abschließen**
   - Klicken Sie auf **Absenden**
   - Die Integration testet die Verbindung
   - Bei Erfolg erscheint das Gerät in der Geräteliste

### Fehlerbehebung bei der Ersteinrichtung

#### "Verbindung fehlgeschlagen"

**Mögliche Ursachen:**
- IP-Adresse ist falsch
- UDP-Port stimmt nicht überein
- Local API ist nicht aktiviert
- Firewall blockiert den Port
- Geräte sind in verschiedenen Netzwerken

**Lösungsschritte:**

1. **IP-Adresse überprüfen**
   ```bash
   # Im Home Assistant Terminal
   ping IP-ADRESSE-DES-GERÄTS
   ```

2. **Port testen**
   ```bash
   nc -u -v IP-ADRESSE PORT
   # Oder verwenden Sie nmap:
   nmap -sU -p PORT IP-ADRESSE
   ```

3. **Manuelle API-Anfrage testen**
   ```bash
   echo '{"id":0,"method":"Marstek.GetDevice","params":{"ble_mac":"0"}}' | nc -u -w1 IP-ADRESSE PORT
   ```

4. **Firewall-Regeln prüfen**
   - Stellen Sie sicher, dass UDP-Port nicht blockiert ist
   - Prüfen Sie Router-Einstellungen
   - Prüfen Sie Home Assistant Firewall

## Verifikation

### Überprüfen Sie die Installation

1. **Gerät finden**
   - Gehen Sie zu **Einstellungen** → **Geräte & Dienste**
   - Klicken Sie auf die Marstek Venus Integration
   - Sie sollten das Gerät mit allen Entitäten sehen

2. **Entitäten prüfen**
   - Gehen Sie zu **Entwicklerwerkzeuge** → **Zustände**
   - Suchen Sie nach "marstek_venus"
   - Sie sollten ca. 20+ Entitäten sehen

3. **Erste Daten überprüfen**
   - `sensor.marstek_venus_battery_soc` - Sollte aktuellen SOC zeigen
   - `sensor.marstek_venus_solar_power` - Sollte aktuelle Solarleistung zeigen
   - `select.marstek_venus_operating_mode` - Sollte aktuellen Modus zeigen

## Dashboard einrichten

### Schnellstart-Dashboard

1. **Neue Dashboard-Ansicht erstellen**
   - Gehen Sie zu **Übersicht**
   - Klicken Sie auf die drei Punkte → **Ansicht hinzufügen**
   - Name: "Marstek Venus"

2. **Beispiel-Karte hinzufügen**
   - Klicken Sie auf **+ Karte hinzufügen**
   - Wählen Sie **Entitäten**
   - Fügen Sie hinzu:
     - `sensor.marstek_venus_battery_soc`
     - `sensor.marstek_venus_solar_power`
     - `sensor.marstek_venus_grid_power`
     - `select.marstek_venus_operating_mode`

3. **Erweiterte Dashboards**
   - Siehe `examples/lovelace_dashboard.yaml` für umfassende Dashboard-Beispiele
   - Kopieren Sie gewünschte Karten in Ihr Dashboard

## Energy Dashboard einrichten

Die Integration ist kompatibel mit dem Home Assistant Energy Dashboard:

1. **Energy Dashboard öffnen**
   - Gehen Sie zu **Energie** in der Seitenleiste
   - Klicken Sie auf **Konfiguration hinzufügen**

2. **Netzverbrauch/-einspeisung**
   - **Netzbezug**: `sensor.marstek_venus_total_grid_input_energy`
   - **Netzeinspeisung**: `sensor.marstek_venus_total_grid_output_energy`

3. **Solarproduktion**
   - **Solar-Erzeugung**: `sensor.marstek_venus_total_solar_energy`

4. **Batteriespeicher**
   - Hinweis: Batterie-Ein-/Ausgabe muss eventuell über Template-Sensoren berechnet werden

5. **Gesamtverbrauch**
   - **Verbrauch**: `sensor.marstek_venus_total_load_energy`

## Automationen einrichten

### Erste Automation erstellen

1. **Automationen öffnen**
   - Gehen Sie zu **Einstellungen** → **Automationen & Szenen**
   - Klicken Sie auf **+ Automation erstellen**

2. **Beispiel: Auto-Modus bei Sonnenaufgang**
   ```yaml
   alias: Marstek Auto-Modus bei Sonnenaufgang
   trigger:
     - platform: sun
       event: sunrise
   action:
     - service: select.select_option
       target:
         entity_id: select.marstek_venus_operating_mode
       data:
         option: "Auto"
   ```

3. **Weitere Beispiele**
   - Siehe `examples/automations.yaml` für 15+ vorkonfigurierte Automationen
   - Kopieren Sie gewünschte Automationen und passen Sie sie an

## Erweiterte Konfiguration

### Services verwenden

Die Integration bietet erweiterte Services für Manual und Passive Mode:

#### Manual Mode mit Zeitplan

```yaml
service: marstek_venus.set_manual_mode
target:
  entity_id: select.marstek_venus_operating_mode
data:
  time_num: 0
  start_time: "08:00"
  end_time: "20:00"
  week_set: 127  # Alle Tage (Mo-So)
  power: 2000
```

#### Passive Mode mit Timer

```yaml
service: marstek_venus.set_passive_mode
target:
  entity_id: select.marstek_venus_operating_mode
data:
  power: 500
  cd_time: 3600  # 1 Stunde
```

### Week Set Berechnung

Der `week_set` Parameter für Manual Mode verwendet binäre Kodierung:

| Tag | Bit | Wert |
|-----|-----|------|
| Montag | 0 | 1 |
| Dienstag | 1 | 2 |
| Mittwoch | 2 | 4 |
| Donnerstag | 3 | 8 |
| Freitag | 4 | 16 |
| Samstag | 5 | 32 |
| Sonntag | 6 | 64 |

**Beispiele:**
- Alle Tage: 127 (1+2+4+8+16+32+64)
- Werktage: 31 (1+2+4+8+16)
- Wochenende: 96 (32+64)
- Nur Montag: 1

## Wartung

### Updates installieren

**Via HACS:**
1. Öffnen Sie HACS → Integrationen
2. Suchen Sie "Marstek Venus"
3. Klicken Sie auf **Update**
4. Starten Sie Home Assistant neu

**Manuell:**
1. Laden Sie die neue Version herunter
2. Ersetzen Sie die Dateien in `custom_components/marstek_venus/`
3. Starten Sie Home Assistant neu

### Logs überprüfen

Bei Problemen prüfen Sie die Logs:

1. **Home Assistant Logs**
   - Gehen Sie zu **Einstellungen** → **System** → **Logs**
   - Suchen Sie nach "marstek_venus"

2. **Debug-Logging aktivieren**
   Fügen Sie zu `configuration.yaml` hinzu:
   ```yaml
   logger:
     default: info
     logs:
       custom_components.marstek_venus: debug
   ```

### Backup erstellen

Sichern Sie regelmäßig:
```bash
# Komplettes Backup
ha backups new --name "vor_marstek_update"

# Nur Konfiguration
cp -r /config/custom_components/marstek_venus ~/backup/
```

## Support

### Hilfe erhalten

1. **Dokumentation**
   - Lesen Sie die vollständige [README.md](README.md)
   - Prüfen Sie [CONTRIBUTING.md](CONTRIBUTING.md) für technische Details

2. **GitHub Issues**
   - Suchen Sie nach ähnlichen Problemen
   - Öffnen Sie ein neues Issue mit detaillierter Beschreibung

3. **Home Assistant Community**
   - Home Assistant Forum
   - Discord Server

### Issue melden

Beim Melden von Problemen bitte angeben:
- Home Assistant Version
- Integration Version
- Marstek Gerätemodell (Venus C/E)
- Firmware-Version
- Fehlermeldungen aus den Logs
- Schritte zur Reproduktion

## Nächste Schritte

Nach erfolgreicher Installation:

1. ✅ Erkunden Sie alle Sensoren und deren Werte
2. ✅ Richten Sie Ihr Energy Dashboard ein
3. ✅ Erstellen Sie Automationen für Ihren Anwendungsfall
4. ✅ Passen Sie das Dashboard an Ihre Bedürfnisse an
5. ✅ Experimentieren Sie mit verschiedenen Betriebsmodi

Viel Erfolg mit Ihrer Marstek Venus Integration! 🎉
