// A single, clean script to manage all client-side functionality.
document.addEventListener('DOMContentLoaded', () => {

    // --- Product Data (in an array) ---
    // This data should ideally come from a server (like your Flask backend),
    // but for a purely client-side script, this is how you manage it.
    const allProducts = [
        { id: '1', name: 'Potato 500g', price: 35, oldPrice: 40, category: 'Vegetables', img: 'P4Mh67A.png' },
        { id: '2', name: 'Tomato 1 kg', price: 28, oldPrice: 30, category: 'Vegetables', img: 'y8L2yvK.png' },
        { id: '3', name: 'Carrot 500g', price: 44, oldPrice: 50, category: 'Vegetables', img: 'nJbB1qg.png' },
        { id: '4', name: 'Spinach 500g', price: 15, oldPrice: 18, category: 'Vegetables', img: 'rL4zP6L.png' },
        { id: '5', name: 'Onion 500g', price: 45, oldPrice: 50, category: 'Vegetables', img: 'cE0Gk8t.png' },
        { id: '6', name: 'Apple 1kg', price: 90, oldPrice: 95, category: 'Fruits', img: 'h5r6c1m.png' },
        { id: '7', name: 'Maggi Noodles 280g', price: 50, oldPrice: 55, category: 'Instant', img: 'g91WkM5.png' },
        { id: '8', name: 'Orange 1kg', price: 75, oldPrice: 80, category: 'Fruits', img: 'i9R3n2i.png' },
        { id: '9', name: 'Banana 1kg', price: 45, oldPrice: 50, category: 'Fruits', img: 'uCjS8E7.png' },
        { id: '10', name: 'Mango 1kg', price: 140, oldPrice: 150, category: 'Fruits', img: '6S331G4.png' },
        { id: '11', name: 'Grapes 500g', price: 65, oldPrice: 70, category: 'Fruits', img: 'Bf1oR9z.png' },
        { id: '12', name: 'Amul Milk 1L', price: 30, oldPrice: 35, category: 'Dairy', img: '4zYg0j1.png' },
        { id: '13', name: 'Paneer 200g', price: 85, oldPrice: 90, category: 'Dairy', img: 'Bf1oR9z.png' },
        { id: '14', name: 'Eggs 12 pcs', price: 85, oldPrice: 90, category: 'Dairy', img: 'uCjS8E7.png' },
        { id: '15', name: 'Cheese 200g', price: 130, oldPrice: 140, category: 'Dairy', img: 'kK5Rz9x.png' },
        { id: '16', name: 'Coca-Cola 1.5L', price: 60, oldPrice: 75, category: 'Drinks', img: 'fO429Qo.png' },
        { id: '17', name: 'Sprite 1.5L', price: 60, oldPrice: 75, category: 'Drinks', img: 'H6sB7qE.png' },
        { id: '18', name: '7 Up 1.5L', price: 70, oldPrice: 76, category: 'Drinks', img: 'uCjS8E7.png' },
        { id: '19', name: 'Fanta 1.5L', price: 65, oldPrice: 70, category: 'Drinks', img: 'uCjS8E7.png' },
        { id: '20', name: 'Basmati Rice 5kg', price: 400, oldPrice: 450, category: 'Grains', img: 'uCjS8E7.png' },
        { id: '21', name: 'Wheat Flour 5kg', price: 230, oldPrice: 250, category: 'Grains', img: 'uCjS8E7.png' },
        { id: '22', name: 'Organic Quinoa 500g', price: 420, oldPrice: 450, category: 'Grains', img: 'uCjS8E7.png' },
        { id: '23', name: 'Brown Rice 1kg', price: 110, oldPrice: 120, category: 'Grains', img: 'uCjS8E7.png' },
        { id: '24', name: 'Barley 1kg', price: 140, oldPrice: 150, category: 'Grains', img: 'uCjS8E7.png' },
        { id: '25', name: 'Brown Bread 400g', price: 45, oldPrice: 50, category: 'Bakery', img: 'uCjS8E7.png' },
        { id: '26', name: 'Butter Croissant 100g', price: 45, oldPrice: 50, category: 'Bakery', img: 'uCjS8E7.png' },
        { id: '27', name: 'Knorr Cup Soup 70g', price: 30, oldPrice: 35, category: 'Instant', img: 'uCjS8E7.png' },
    ];

    // --- Utility Functions ---
    function getProductById(id) {
        return allProducts.find(product => product.id === id);
    }

    function updateCartBadge() {
        const badge = document.getElementById("cart-count");
        const cart = JSON.parse(localStorage.getItem("cart")) || [];
        if (badge) badge.textContent = cart.length;
    }

    function addToCart(productId) {
        let cart = JSON.parse(localStorage.getItem("cart")) || [];
        const product = getProductById(productId);

        if (product) {
            const existing = cart.find(item => item.id === product.id);
            if (existing) {
                existing.quantity++;
            } else {
                cart.push({
                    id: product.id,
                    name: product.name,
                    price: product.price,
                    image: `{{ url_for('static', filename='images/${product.img}') }}`,
                    quantity: 1
                });
            }
            localStorage.setItem("cart", JSON.stringify(cart));
            updateCartBadge();
            alert(`${product.name} added to cart`);
        }
    }

    // --- Event Listeners and Initializers ---

    // This listener handles the "Add to Cart" button on any product card on any page
    const addButtons = document.querySelectorAll(".add-to-cart-btn");
    addButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const productId = btn.dataset.id;
            const product = {
                id: btn.dataset.id,
                name: btn.dataset.name,
                price: parseFloat(btn.dataset.price),
                image: btn.dataset.image,
                quantity: 1
            };

            let cart = JSON.parse(localStorage.getItem("cart")) || [];
            const existing = cart.find(item => item.id === product.id);
            if (existing) {
                existing.quantity++;
            } else {
                cart.push(product);
            }
            localStorage.setItem("cart", JSON.stringify(cart));
            updateCartBadge();
            alert(`${product.name} added to cart!`);
        });
    });

    // Initial call to update the cart badge on page load
    updateCartBadge();

});

