import penambahan
import pengurangan
import perkalian
import pembagian

a = float(input("Masukkan angka pertama : "))
b = float(input("Masukkan angka kedua   : "))

print(f"Penambahan dari {a} dan {b} adalah {penambahan.penambahan(a, b)}")
print(f"Pengurangan dari {a} dan {b} adalah {pengurangan.pengurangan(a, b)}")
print(f"Perkalian dari {a} dan {b} adalah {perkalian.perkalian(a, b)}")
print(f"Pembagian dari {a} dan {b} adalah {pembagian.pembagian(a, b)}")
