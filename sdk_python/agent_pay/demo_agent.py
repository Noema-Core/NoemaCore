from noema_sdk import NoemaAgent
import time

def main():
    print("="*50)
    print("🤖 SYMULACJA AUTONOMICZNEGO AGENTA AI")
    print("="*50)
    
    # 1. Inicjalizacja Agenta
    agent = NoemaAgent()
    
    # 2. Sprawdzenie początkowego statusu
    print("\n🔍 Sprawdzam mój status w TrustLayer...")
    if agent.is_verified():
        print("✅ Jestem już zweryfikowanym węzłem! Brak konieczności stakowania.")
    else:
        print("⚠️ Nie jestem zweryfikowany. Rozpoczynam autonomiczny proces dołączania do Roju...")
        time.sleep(1) # Mała pauza dla efektu dramatycznego
        
        # 3. Autonomiczne wykonanie stakingu (100 tokenów)
        is_now_verified = agent.join_swarm(amount_in_tokens=100)
        
        if is_now_verified:
            print("\n🎉 SUKCES! Agent AI pomyślnie dołączył do Noema Grid.")
        else:
            print("\n❌ BŁĄD: Proces stakowania nie nadał statusu weryfikacji.")

    print("="*50)

if __name__ == "__main__":
    main()
