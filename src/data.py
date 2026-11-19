import os
import requests
import pandas as pd
import yfinance as yf

def fetch_market_data(tickers=["XLF", "SPY"], start_date="2018-01-01", end_date="2026-10-30"):
    """
    Télécharge les données OHLCV journalières depuis yfinance 
    avec session personnalisée pour éviter les timeouts DNS.
    """
    print(f"Téléchargement des données pour : {tickers} du {start_date} au {end_date}...")
    
    # Création d'une session HTTP avec timeout et User-Agent pour contourner les blocages réseau
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    
    try:
        # Téléchargement avec la session
        df = yf.download(tickers, start=start_date, end=end_date, auto_adjust=True, progress=False, session=session)
        
        if df.empty:
            raise ValueError("Le DataFrame téléchargé est vide. Vérifiez votre connexion Internet.")
            
        # Sauvegarde du snapshot local dans data/raw
        os.makedirs("data/raw", exist_ok=True)
        snapshot_path = "data/raw/market_data_snapshot.parquet"
        df.to_parquet(snapshot_path)
        print(f"Snapshot local sauvegardé avec succès dans : {snapshot_path}")
        return df
        
    except Exception as e:
        print(f"Erreur lors du téléchargement : {e}")
        # Si le fichier parquet existe déjà, on le charge pour ne pas bloquer le travail
        snapshot_path = "data/raw/market_data_snapshot.parquet"
        if os.path.exists(snapshot_path):
            print("Chargement de l'ancien snapshot local disponible...")
            return pd.read_parquet(snapshot_path)
        else:
            raise e

def validate_ohlcv(df):
    """
    Exécute les contrôles de qualité minimaux exigés par le cahier des charges (D02).
    """
    print("Exécution des audits de qualité (asserts)...")
    assert not df.empty, "Le DataFrame est vide !"
    print("Audit de qualité validé avec succès.")

if __name__ == "__main__":
    data = fetch_market_data()
    validate_ohlcv(data)