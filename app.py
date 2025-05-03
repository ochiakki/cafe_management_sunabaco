from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

DB_NAME = "cafe_management.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    return render_template("index.html")

# 材料一覧表示
@app.route("/materials")
def view_materials():
    conn = get_db_connection()
    materials = conn.execute("SELECT * FROM materials").fetchall()
    conn.close()
    return render_template("view_materials.html", materials=materials)

# 材料追加
@app.route("/add_material", methods=["GET", "POST"])
def add_material():
    if request.method == "POST":
        name = request.form["name"]
        unit = request.form["unit"]
        stock = request.form["stock"]

        conn = get_db_connection()
        conn.execute("INSERT INTO materials (name, unit, stock) VALUES (?, ?, ?)", (name, unit, stock))
        conn.commit()
        conn.close()
        return redirect(url_for("view_materials"))
    return render_template("add_material.html")

# 材料編集
@app.route("/edit_material/<int:id>", methods=["GET", "POST"])
def edit_material(id):
    conn = get_db_connection()
    material = conn.execute("SELECT * FROM materials WHERE id = ?", (id,)).fetchone()
    if request.method == "POST":
        name = request.form["name"]
        unit = request.form["unit"]
        stock = request.form["stock"]
        conn.execute("UPDATE materials SET name = ?, unit = ?, stock = ? WHERE id = ?",
                     (name, unit, stock, id))
        conn.commit()
        conn.close()
        return redirect(url_for("view_materials"))
    conn.close()
    return render_template("edit_material.html", material=material)

# 材料削除
@app.route("/delete_material/<int:id>")
def delete_material(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM materials WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("view_materials"))

# 商品一覧表示
@app.route("/products")
def view_products():
    conn = get_db_connection()
    products = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    return render_template("view_products.html", products=products)

# 商品追加
@app.route("/add_product", methods=["GET", "POST"])
def add_product():
    if request.method == "POST":
        name = request.form["name"]
        price = request.form["price"]

        conn = get_db_connection()
        conn.execute("INSERT INTO products (name, price) VALUES (?, ?)", (name, price))
        conn.commit()
        conn.close()
        return redirect(url_for("view_products"))
    return render_template("add_product.html")

@app.route('/product_recipes/add', methods=['GET', 'POST'])
def add_product_recipe():
    conn = sqlite3.connect('cafe_management.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    if request.method == 'POST':
        product_id = request.form['product_id']
        selected_material_ids = request.form.getlist('material_ids')

        for material_id in selected_material_ids:
            quantity = request.form.get(f'quantity_{material_id}')
            if quantity and float(quantity) > 0:
                cur.execute(
                    'INSERT INTO product_recipes (product_id, material_id, quantity) VALUES (?, ?, ?)',
                    (product_id, material_id, quantity)
                )

        conn.commit()
        conn.close()
        return redirect(url_for('view_product_recipes'))

    # GETメソッド
    cur.execute('SELECT * FROM products')
    products = cur.fetchall()
    cur.execute('SELECT * FROM materials')
    materials = cur.fetchall()
    conn.close()

    return render_template('add_product_recipe.html', products=products, materials=materials)

@app.route('/view_product_recipes')
def view_product_recipes():
    conn = get_db_connection()
    cur = conn.cursor()
    recipes = cur.execute('''
        SELECT pr.id, p.name AS product_name, m.name AS material_name, pr.quantity
        FROM product_recipes pr
        JOIN products p ON pr.product_id = p.id
        JOIN materials m ON pr.material_id = m.id
    ''').fetchall()
    conn.close()
    return render_template('view_product_recipes.html', recipes=recipes)


@app.route('/edit_product_recipe/<int:recipe_id>', methods=['GET', 'POST'])
def edit_product_recipe(recipe_id):
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        product_id = request.form['product_id']
        material_id = request.form['material_id']
        quantity = request.form['quantity']
        cur.execute('''
            UPDATE product_recipes
            SET product_id = ?, material_id = ?, quantity = ?
            WHERE id = ?
        ''', (product_id, material_id, quantity, recipe_id))
        conn.commit()
        conn.close()
        return redirect(url_for('view_product_recipes'))

    # 編集対象を取得
    recipe = cur.execute('SELECT * FROM product_recipes WHERE id = ?', (recipe_id,)).fetchone()
    products = cur.execute('SELECT * FROM products').fetchall()
    materials = cur.execute('SELECT * FROM materials').fetchall()
    conn.close()
    return render_template('edit_product_recipe.html', recipe=recipe, products=products, materials=materials)


@app.route('/delete_product_recipe/<int:recipe_id>', methods=['POST'])
def delete_product_recipe(recipe_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM product_recipes WHERE id = ?', (recipe_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('view_product_recipes'))


if __name__ == "__main__":
    app.run(debug=True)
