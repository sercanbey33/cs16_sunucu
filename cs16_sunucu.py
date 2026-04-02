#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CS 1.6 RCON Yönetim Aracı - Termux için
Root erişimi gerektirmez - by SeRCaN BeY ( NxYFLuX Official )
"""

import socket
import struct
import time
import sys
import select
import threading
import re

class CS16RCON:
    def __init__(self, host, port, password):
        self.host = host
        self.port = port
        self.password = password
        self.socket = None
        self.request_id = 0
        self.connected = False
        self.logs = []
        self.log_thread = None
        self.running = False

    def connect(self):
        """Sunucuya bağlan"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.settimeout(5.0)
            self.socket.connect((self.host, self.port))

            
            response = self.send_command("", authenticate=True)
            if response:
                self.connected = True
                print(f"✓ {self.host}:{self.port} sunucusuna bağlanıldı")
                return True
            else:
                print("✗ RCON şifresi yanlış veya sunucu yanıt vermiyor")
                return False
        except Exception as e:
            print(f"✗ Bağlantı hatası: {e}")
            return False

    def disconnect(self):
        """Bağlantıyı kapat"""
        self.running = False
        if self.log_thread:
            self.log_thread.join(timeout=2)
        if self.socket:
            self.socket.close()
        self.connected = False
        print("Bağlantı kapatıldı")

    def send_command(self, command, authenticate=False):
        """RCON komutu gönder"""
        if not self.socket:
            return None

        self.request_id += 1
        request_id = self.request_id

        
        if authenticate:
            packet_type = 3  
            command = self.password
        else:
            packet_type = 2  

        # Paketi oluştur
        payload = struct.pack('<ii', request_id, packet_type) + command.encode('utf-8') + b'\x00\x00'
        packet_size = len(payload)
        packet = struct.pack('<i', packet_size) + payload

        try:
            self.socket.send(packet)

            
            self.socket.settimeout(5.0)
            data = self.socket.recv(4096)

            if len(data) < 8:
                return None

            
            size = struct.unpack('<i', data[:4])[0]
            response_id = struct.unpack('<i', data[4:8])[0]

            if response_id == -1:
                return None  

            response_body = data[12:].decode('utf-8', errors='ignore').strip('\x00')
            return response_body

        except socket.timeout:
            return None
        except Exception as e:
            return None

    def execute(self, command):
        """Komut çalıştır ve sonucu döndür"""
        if not self.connected:
            print("Sunucuya bağlı değilsiniz!")
            return None
        return self.send_command(command)

    def get_status(self):
        """Sunucu durumunu al"""
        return self.execute("status")

    def get_players(self):
        """Oyuncu listesini al"""
        status = self.get_status()
        if not status:
            return []

        players = []
        lines = status.split('\n')
        player_pattern = re.compile(r'#\s*(\d+)\s+\"(.+?)\"\s+(\S+)\s+(\d+)\s+(\d+)\s+(\S+)\s+(\d+)\s+(\S+)')

        for line in lines:
            match = player_pattern.search(line)
            if match:
                players.append({
                    'id': match.group(1),
                    'name': match.group(2),
                    'steamid': match.group(3),
                    'time': match.group(4),
                    'ping': match.group(5),
                    'loss': match.group(6),
                    'ip': match.group(8) if len(match.groups()) > 7 else 'N/A'
                })
        return players

    def kick_player(self, player_id_or_name):
        """Oyuncu at"""
        result = self.execute(f"kick {player_id_or_name}")
        print(f"Oyuncu atıldı: {player_id_or_name}")
        return result

    def ban_player(self, player_id_or_name, time_minutes=0):
        """Oyuncu yasakla (0 = kalıcı)"""
        if time_minutes > 0:
            result = self.execute(f"banid {time_minutes} {player_id_or_name}")
        else:
            result = self.execute(f"banid 0 {player_id_or_name}")
            self.execute(f"kick {player_id_or_name}")
        print(f"Oyuncu yasaklandı: {player_id_or_name}")
        return result

    def mute_player(self, player_id, mute=True):
        """Oyuncu sustur/aç"""
        cmd = "mute" if mute else "unmute"
        result = self.execute(f"{cmd} {player_id}")
        status = "susturuldu" if mute else "susturma kaldırıldı"
        print(f"Oyuncu {player_id} {status}")
        return result

    def change_map(self, map_name):
        """Harita değiştir"""
        result = self.execute(f"changelevel {map_name}")
        print(f"Harita değiştirildi: {map_name}")
        return result

    def say_to_all(self, message):
        """Tüm oyunculara mesaj gönder"""
        result = self.execute(f"say {message}")
        print(f"Mesaj gönderildi: {message}")
        return result

    def set_hostname(self, name):
        """Sunucu ismini değiştir"""
        # HATA DÜZELTİLDİ: İçerideki tırnaklar tek tırnak yapıldı
        result = self.execute(f"hostname '{name}'")
        print(f"Sunucu ismi değiştirildi: {name}")
        return result

    def set_password(self, password):
        """Sunucu şifresini değiştir"""
        if password:
            # HATA DÜZELTİLDİ: İçerideki tırnaklar tek tırnak yapıldı
            result = self.execute(f"sv_password '{password}'")
            print(f"Sunucu şifresi ayarlandı: {password}")
        else:
            result = self.execute("sv_password ''")
            print("Sunucu şifresi kaldırıldı")
        return result

    def get_logs(self):
        """Sunucu loglarını al"""
        return self.execute("log")

    def start_log_monitor(self):
        """Log izlemeyi başlat"""
        self.running = True
        self.log_thread = threading.Thread(target=self._monitor_logs)
        self.log_thread.daemon = True
        self.log_thread.start()
        print("Log izleme başlatıldı (Ctrl+C ile durdurun)")

    def _monitor_logs(self):
        """Log izleme thread'i"""
        last_logs = ""
        while self.running:
            try:
                logs = self.get_logs()
                if logs and logs != last_logs:
                    new_part = logs[len(last_logs):] if last_logs else logs
                    if new_part:
                        print(f"\n[LOG] {new_part}")
                    last_logs = logs
                time.sleep(2)
            except:
                pass

    def show_menu(self):
        """İnteraktif menü"""
        print("""
╔══════════════════════════════════════════════════════════════╗
║           CS 1.6 RCON YÖNETİM ARACI - TERMUX  by SeRCaN BeY                ║
╠══════════════════════════════════════════════════════════════╣
║  1. Sunucu Durumu (status)                                    ║
║  2. Oyuncu Listesi                                            ║
║  3. Oyuncu At (kick)                                          ║
║  4. Oyuncu Yasakla (ban)                                      ║
║  5. Oyuncu Sustur (mute)                                      ║
║  6. Harita Değiştir                                           ║
║  7. Sunucu İsmi Değiştir                                      ║
║  8. Sunucu Şifresi Değiştir                                   ║
║  9. Mesaj Gönder (say)                                        ║
║  10. Logları İzle                                             ║
║  11. Özel Komut Gönder                                        ║
║  0. Çıkış                                                     ║
╚══════════════════════════════════════════════════════════════╝
        """)

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║       COUNTER-STRIKE 1.6 RCON YÖNETİM ARACI                  ║
║              Termux için - Root Gerektirmez by SeRCaN BeY             ║
╚══════════════════════════════════════════════════════════════╝
    """)

    # Sunucu bilgilerini al
    host = input("Sunucu IP: ").strip()
    port = input("RCON Port (varsayılan 27015): ").strip()
    port = int(port) if port else 27015
    password = input("RCON Şifresi: ").strip()

    # Bağlan
    rcon = CS16RCON(host, port, password)
    if not rcon.connect():
        sys.exit(1)

    while True:
        rcon.show_menu()
        choice = input("Seçiminiz: ").strip()

        if choice == "1":
            status = rcon.get_status()
            print("\n--- SUNUCU DURUMU ---")
            print(status if status else "Durum alınamadı")

        elif choice == "2":
            players = rcon.get_players()
            print("\n--- OYUNCU LİSTESİ ---")
            if players:
                print(f"{'ID':<5} {'İsim':<20} {'SteamID':<20} {'IP':<15} {'Ping':<6}")
                print("-" * 70)
                for p in players:
                    print(f"{p['id']:<5} {p['name']:<20} {p['steamid']:<20} {p['ip']:<15} {p['ping']:<6}")
            else:
                print("Aktif oyuncu yok")

        elif choice == "3":
            target = input("Oyuncu ID veya İsmi: ").strip()
            rcon.kick_player(target)

        elif choice == "4":
            target = input("Oyuncu ID veya SteamID: ").strip()
            time_input = input("Yasaklama süresi (dakika, 0=kalıcı): ").strip()
            time_min = int(time_input) if time_input.isdigit() else 0
            rcon.ban_player(target, time_min)

        elif choice == "5":
            pid = input("Oyuncu ID: ").strip()
            action = input("Sustur (1) / Susturma Kaldır (0): ").strip()
            rcon.mute_player(pid, action == "1")

        elif choice == "6":
            map_name = input("Harita adı (örn: de_dust2): ").strip()
            rcon.change_map(map_name)

        elif choice == "7":
            name = input("Yeni sunucu ismi: ").strip()
            rcon.set_hostname(name)

        elif choice == "8":
            pwd = input("Yeni şifre (boş bırak=şifre kaldır): ").strip()
            rcon.set_password(pwd)

        elif choice == "9":
            msg = input("Mesajınız: ").strip()
            rcon.say_to_all(msg)

        elif choice == "10":
            rcon.start_log_monitor()
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                rcon.running = False
                print("\nLog izleme durduruldu")

        elif choice == "11":
            cmd = input("Komut: ").strip()
            result = rcon.execute(cmd)
            print(f"Sonuç: {result}")

        elif choice == "0":
            rcon.disconnect()
            print("Güle güle!")
            break

        input("\nDevam etmek için Enter'a basın...")

if __name__ == "__main__":
    main()
