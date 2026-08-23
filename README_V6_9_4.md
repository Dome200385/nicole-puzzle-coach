# Nicole Puzzle Coach V6.9.4 – App Navigation Fix

Fix für die mobile PWA-Navigation. In V6.9.3 wurde `initAppNavigation()` ausgeführt, bevor die Bottom-Navigation im DOM vorhanden war. Dadurch wurden keine Click-Listener an Heute / Training / WM / Fortschritt / Mehr gebunden. V6.9.4 initialisiert Navigation und Startlogik erst nach `DOMContentLoaded`. Service-Worker-Cache auf v694 erhöht. Coach-, Readiness- und MSP-Berechnungen bleiben unverändert.
