// Wait for the entire page to load before running the script
document.addEventListener('DOMContentLoaded', () => {

    // Select all "Add" buttons on the page
    const addToCartButtons = document.querySelectorAll('.add-to-cart-btn');

    // Loop through each button and add a click event listener
    addToCartButtons.forEach(button => {
        button.addEventListener('click', (event) => {
            // Get the product data from the button's data attributes
            const productId = button.dataset.id;
            const productName = button.dataset.name;
            const productPrice = parseFloat(button.dataset.price);
            const productImage = button.dataset.image;

            // Get the current cart from localStorage
            let cart = JSON.parse(localStorage.getItem('cart')) || [];
            
            // Check if the item is already in the cart
            const existingItem = cart.find(item => item.id === productId);

            if (existingItem) {
                // If it exists, just increase the quantity
                existingItem.quantity++;
            } else {
                // If it doesn't exist, add it as a new item
                cart.push({
                    id: productId,
                    name: productName,
                    price: productPrice,
                    image: productImage,
                    quantity: 1
                });
            }

            // Save the updated cart back to localStorage
            localStorage.setItem('cart', JSON.stringify(cart));

            // Show a confirmation to the user
            alert(`Added ${productName} to your cart!`);
            console.log('Cart updated:', cart);

            // You can also add a visual indicator here, like updating a cart icon
            // document.getElementById('cart-item-count').textContent = cart.length;
        });
    });

});