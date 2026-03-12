import sqlite3
import os

DB = "inventory.db"

def connect_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    sql = """
    CREATE TABLE IF NOT EXISTS products(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        price REAL NOT NULL,
        quantity INTEGER NOT NULL
    );

    CREATE TABLE IF NOT EXISTS purchases(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(product_id) REFERENCES products(id)
    );
    """
    with connect_db() as conn:
        conn.executescript(sql)


def insert_sample_products():

    products = [
        ("Laptop",50000,20),
        ("Mouse",500,50),
        ("Keyboard",1200,40),
        ("Monitor",10000,15),
        ("Printer",8000,10),
        ("USB Cable",150,100),
        ("Hard Disk",4000,25),
        ("SSD",6000,20),
        ("RAM 8GB",2500,30),
        ("RAM 16GB",4500,25),
        ("Graphics Card",30000,10),
        ("Webcam",2000,18),
        ("Headphones",1500,35),
        ("Speaker",1800,30),
        ("Router",2500,20),
        ("Power Bank",1200,40),
        ("Smartphone",20000,15),
        ("Tablet",15000,12),
        ("Charger",600,60),
        ("Microphone",2200,15),
        ("Projector",35000,5),
        ("Extension Board",400,50),
        ("LED Lamp",350,45),
        ("Fan",1800,25),
        ("Calculator",300,70),
        ("Notebook Pack",250,80),
        ("Pen Pack",100,90),
        ("Desk Organizer",500,35),
        ("Office Chair",7000,12),
        ("Study Table",9000,10)
    ]

    with connect_db() as conn:

        count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]

        if count == 0:
            conn.executemany(
                "INSERT INTO products(name,price,quantity) VALUES(?,?,?)",
                products
            )


def display_products(products):

    if not products:
        print("No products available.\n")
        return

    print("\n"+"="*60)
    print(f"{'ID':<5}{'Name':<20}{'Price':<12}{'Quantity':<10}")
    print("="*60)

    for p in products:
        print(f"{p['id']:<5}{p['name']:<20}{p['price']:<12.2f}{p['quantity']:<10}")

    print("="*60+"\n")


def list_products():
    with connect_db() as conn:
        return conn.execute("SELECT * FROM products").fetchall()


def add_product(name, price, qty):
    try:
        with connect_db() as conn:
            conn.execute(
                "INSERT INTO products(name,price,quantity) VALUES(?,?,?)",
                (name,price,qty)
            )
    except sqlite3.IntegrityError:
        print("Product already exists.")


def update_product(pid, name=None, price=None, qty=None):

    fields=[]
    params=[]

    if name:
        fields.append("name=?")
        params.append(name)

    if price:
        fields.append("price=?")
        params.append(price)

    if qty:
        fields.append("quantity=?")
        params.append(qty)

    if not fields:
        print("Nothing to update.")
        return

    params.append(pid)

    sql=f"UPDATE products SET {', '.join(fields)} WHERE id=?"

    with connect_db() as conn:
        conn.execute(sql,params)


def delete_product(pid):
    with connect_db() as conn:
        r=conn.execute("DELETE FROM products WHERE id=?",(pid,))
        if r.rowcount==0:
            print("Product not found")
        else:
            print("Product deleted successfully")


def buy_product(pid, qty):

    with connect_db() as conn:

        product=conn.execute(
            "SELECT quantity FROM products WHERE id=?",
            (pid,)
        ).fetchone()

        if not product:
            print("Product does not exist")
            return

        if product["quantity"] < qty:
            print("Not enough stock")
            return

        conn.execute(
            "UPDATE products SET quantity=quantity-? WHERE id=?",
            (qty,pid)
        )

        conn.execute(
            "INSERT INTO purchases(product_id,quantity) VALUES(?,?)",
            (pid,qty)
        )

        print("Purchase successful")


def view_history():

    with connect_db() as conn:

        rows=conn.execute("""
        SELECT pu.id,pu.product_id,p.name,pu.quantity,pu.purchased_at
        FROM purchases pu
        LEFT JOIN products p ON pu.product_id=p.id
        """).fetchall()

        if not rows:
            print("No purchase history\n")
            return

        print("\n"+"="*80)
        print(f"{'PurchaseID':<12}{'ProductID':<10}{'Name':<20}{'Qty':<8}{'Date'}")
        print("="*80)

        for r in rows:
            name=r["name"] if r["name"] else "(deleted)"
            print(f"{r['id']:<12}{r['product_id']:<10}{name:<20}{r['quantity']:<8}{r['purchased_at']}")

        print("="*80+"\n")


def seller_menu():

    while True:

        print("Seller Menu")
        print("1 Add Product")
        print("2 Update Product")
        print("3 Delete Product")
        print("4 List Products")
        print("5 Sales History")
        print("6 Back")

        ch=input("Enter choice: ")

        if ch=="1":

            name=input("Name: ")
            price=float(input("Price: "))
            qty=int(input("Quantity: "))
            add_product(name,price,qty)

        elif ch=="2":

            pid=int(input("Product ID: "))
            name=input("New name (blank skip): ")
            price=input("New price: ")
            qty=input("New qty: ")

            price=float(price) if price else None
            qty=int(qty) if qty else None
            name=name if name else None

            update_product(pid,name,price,qty)

        elif ch=="3":

            pid=int(input("Product ID: "))
            delete_product(pid)

        elif ch=="4":

            display_products(list_products())

        elif ch=="5":

            view_history()

        elif ch=="6":

            break


def customer_menu():

    while True:

        print("Customer Menu")
        print("1 View Products")
        print("2 Buy Product")
        print("3 Back")

        ch=input("Enter choice: ")

        if ch=="1":

            display_products(list_products())

        elif ch=="2":

            pid=int(input("Product ID: "))
            qty=int(input("Quantity: "))
            buy_product(pid,qty)

        elif ch=="3":

            break


def main():

    create_tables()
    insert_sample_products()

    while True:

        print("\nInventory Management System")
        print("1 Seller")
        print("2 Customer")
        print("3 Exit")

        ch=input("Enter choice: ")

        if ch=="1":

            seller_menu()

        elif ch=="2":

            customer_menu()

        elif ch=="3":

            break


if __name__ == "__main__":
    main()