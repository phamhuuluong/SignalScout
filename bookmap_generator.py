import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

# MARK: - HUB BOOKMAP GENERATOR DEMO
# Script nay minh hoa cach Server (Hub) tao ra anh Heatmap thanh khoan 
# tu du lieu Level 2 (Order Book) va luu thanh file latest.png de iOS App tai ve hien thi.
# Yeu cau thu vien: pip install numpy matplotlib seaborn

def generate_mock_order_book_matrix(time_steps=60, price_levels=50):
    """
    Gia lap ma tran Sổ Lệnh (Order Book).
    Thuc te: Ban phai hung WebSocket L2 (Binance/CME), tich luy Volume vao ma tran nay.
    """
    matrix = np.random.rand(price_levels, time_steps) * 10
    
    # Tao 1 vung khang cu/ho tro gia vo (Thanh khoan day dac)
    matrix[10:13, :] += 50  # Support
    matrix[40:42, :] += 40  # Resistance
    
    # Tao 1 duong gia dang di chuyen (Day la duong Chart Line chay de len Heatmap)
    price_path = np.linspace(20, 30, time_steps) + np.sin(np.linspace(0, 5, time_steps)) * 5
    
    return matrix, price_path

def create_heatmap_image(output_path="static/bookmap/latest.png"):
    print("Dang tao Bookmap Heatmap...")
    matrix, price_path = generate_mock_order_book_matrix()
    
    # Thiet lap bieu do
    plt.figure(figsize=(10, 6), dpi=150) # Kich thuoc 1500x900px, sac net cho iPhone
    
    # Ve Heatmap thanh khoan
    # Dung mau 'magma' hoac 'inferno' de giong voi Bookmap chuyen nghiep nhat
    sns.heatmap(matrix, cmap="inferno", cbar=True, xticklabels=False, yticklabels=False)
    
    # Ve chong duong Gia len ma tran nhiet (Mau trang cho de nhin)
    plt.plot(price_path, color='white', linewidth=2, label="Current Price")
    
    plt.title(f"Liquidity Heatmap (L2 Sổ Lệnh) - {datetime.now().strftime('%H:%M:%S')}", color='white')
    plt.legend(loc="upper right")
    
    # Dark mode theing
    plt.gca().set_facecolor('black')
    plt.gcf().patch.set_facecolor('black')
    
    # Vao muc static/bookmap de luu
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Luu hinh anh lai
    plt.savefig(output_path, facecolor='black', bbox_inches='tight')
    plt.close()
    print(f"Da xuat thanh cong: {output_path}")

if __name__ == "__main__":
    # Chay thu
    create_heatmap_image()
    # Cach su dung thuc te: Cai dat 1 Timer loop (Vi du: 30 giay chay ham nay 1 lan)
    # Va dung FastAPI serve thu muc "static" de iOS App the truy cap duoc url:
    # https://hub.lomofx.com/api/v1/bookmap/latest.png
