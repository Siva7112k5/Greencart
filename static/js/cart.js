// ========================= cart.js ===========================
document.addEventListener("DOMContentLoaded", () => {
    // ------------------ DOM Elements ------------------
    const cartList = document.getElementById("cart-items-list");
    const cartItemCount = document.getElementById("cart-item-count");
    const priceTotal = document.getElementById("price-total");
    const taxAmount = document.getElementById("tax-amount");
    const totalAmountSpan = document.getElementById("total-amount");
    const paymentSelect = document.getElementById("payment-select");
    const placeOrderBtn = document.querySelector(".place-order-btn");

    // ---------------- Custom Modal for Alerts ----------------
    const modalContainer = document.createElement('div');
    modalContainer.id = 'custom-alert-modal';
    modalContainer.style.cssText = `
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.6); display: none; justify-content: center;
        align-items: center; z-index: 1000;
    `;
    const modalContent = document.createElement('div');
    modalContent.style.cssText = `
        background: white; padding: 20px; border-radius: 8px; max-width: 400px;
        width: 90%; box-shadow: 0 4px 12px rgba(0,0,0,0.2); text-align: center;
    `;
    const modalMessage = document.createElement('p');
    modalMessage.style.marginBottom = '20px';
    const modalButton = document.createElement('button');
    modalButton.textContent = 'OK';
    modalButton.style.cssText = `
        background: #10B981; color: white; padding: 10px 20px; border: none;
        border-radius: 6px; cursor: pointer; font-weight: bold;
    `;
    modalButton.onclick = () => modalContainer.style.display = 'none';

    modalContent.appendChild(modalMessage);
    modalContent.appendChild(modalButton);
    modalContainer.appendChild(modalContent);
    document.body.appendChild(modalContainer);

    function showCustomAlert(message, type = 'error') {
        modalMessage.textContent = message;
        modalContent.style.borderTop = `5px solid ${type === 'success' ? '#10B981' : '#EF4444'}`;
        modalContainer.style.display = 'flex';
    }

    // ---------------- Retrieve Cart ----------------
    let cart = JSON.parse(localStorage.getItem("cart")) || [];
    let finalTotalAmount = 0; // global total with tax

    // ==========================================================
    // 1. RENDER CART
    // ==========================================================
    function renderCart() {
        cartList.innerHTML = "";
        let totalPrice = 0;

        // If empty
        if (cart.length === 0) {
            cartList.innerHTML =
                "<p class='text-center py-4 text-gray-500'>Your cart is empty. <a href='/products' class='text-green-600 font-semibold'>Start Shopping</a></p>";
            cartItemCount.textContent = "0 Items";
            priceTotal.textContent = "₹0.00";
            taxAmount.textContent = "₹0.00";
            totalAmountSpan.textContent = "₹0.00";
            placeOrderBtn.disabled = true;
            placeOrderBtn.classList.add('opacity-50', 'cursor-not-allowed');
            finalTotalAmount = 0;
            return;
        }

        placeOrderBtn.disabled = false;
        placeOrderBtn.classList.remove('opacity-50', 'cursor-not-allowed');

        // Render each product in cart
        cart.forEach((item, index) => {
            const itemPrice = parseFloat(item.price);
            if (isNaN(itemPrice)) {
                console.error(`Invalid price for ${item.name}`);
                return;
            }

            const subtotal = itemPrice * item.quantity;
            totalPrice += subtotal;

            // ✅ Use real product image path
            const imagePath = `/static/images/${item.img}`;

            const cartItem = document.createElement("div");
            cartItem.classList.add("cart-item");

            cartItem.innerHTML = `
                <div class="item-details" data-product-id="${item.id}">
                    <img src="${imagePath}" alt="${item.name}" class="item-image">
                    <div class="item-info">
                        <h4 class="item-name">${item.name}</h4>
                        <p class="item-price">₹${itemPrice.toFixed(2)}</p>
                    </div>
                </div>
                <div class="item-quantity">
                    <button class="quantity-btn decrease" data-index="${index}">-</button>
                    <span class="quantity-value">${item.quantity}</span>
                    <button class="quantity-btn increase" data-index="${index}">+</button>
                </div>
                <span class="item-subtotal">₹${subtotal.toFixed(2)}</span>
                <button class="item-remove" data-index="${index}">Remove</button>
            `;

            cartList.appendChild(cartItem);
        });

        // ---- Totals ----
        const taxRate = 0.02;  // 2%
        const tax = totalPrice * taxRate;
        finalTotalAmount = totalPrice + tax;

        cartItemCount.textContent = `${cart.length} Item${cart.length !== 1 ? 's' : ''}`;
        priceTotal.textContent = `₹${totalPrice.toFixed(2)}`;
        taxAmount.textContent = `₹${tax.toFixed(2)}`;
        totalAmountSpan.textContent = `₹${finalTotalAmount.toFixed(2)}`;

        attachQuantityListeners();
    }

    // ==========================================================
    // 2. QUANTITY & REMOVE BUTTONS
    // ==========================================================
    function attachQuantityListeners() {
        document.querySelectorAll(".quantity-btn.decrease").forEach(button => {
            button.onclick = () => {
                const index = parseInt(button.dataset.index);
                if (cart[index].quantity > 1) {
                    cart[index].quantity--;
                } else {
                    cart.splice(index, 1);  // remove if quantity goes to 0
                }
                saveCart();
            };
        });

        document.querySelectorAll(".quantity-btn.increase").forEach(button => {
            button.onclick = () => {
                const index = parseInt(button.dataset.index);
                cart[index].quantity++;
                saveCart();
            };
        });

        document.querySelectorAll(".item-remove").forEach(button => {
            button.onclick = () => {
                const index = parseInt(button.dataset.index);
                cart.splice(index, 1);
                saveCart();
            };
        });
    }

    // ==========================================================
    // 3. SAVE CART & PLACE ORDER
    // ==========================================================
    function saveCart() {
        localStorage.setItem("cart", JSON.stringify(cart));
        renderCart();
    }

    placeOrderBtn.addEventListener("click", placeOrder);

    async function placeOrder() {
        if (cart.length === 0) {
            showCustomAlert("Your cart is empty. Cannot place an order.", 'error');
            return;
        }

        const cartItemsForServer = cart.map(item => ({
            product_id: parseInt(item.id),
            quantity: parseInt(item.quantity)
        }));

        const orderData = {
            cart_items: cartItemsForServer,
            total_amount: parseFloat(finalTotalAmount.toFixed(2)),
            payment_method: paymentSelect.value
        };

        placeOrderBtn.textContent = "Placing Order...";
        placeOrderBtn.disabled = true;

        try {
            const response = await fetch('/place_order', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(orderData)
            });

            const contentType = response.headers.get("content-type");
            let result = {};
            if (contentType && contentType.includes("application/json")) {
                result = await response.json();
            } else {
                throw new Error("Non-JSON response from server.");
            }

            if (response.ok && result.status === 'success') {
                showCustomAlert(`Order #${result.order_id} placed successfully!`, 'success');
                localStorage.removeItem("cart");
                cart = [];
                setTimeout(() => window.location.href = result.redirect_url, 1500);
            } else {
                showCustomAlert(`Order failed: ${result.message || 'Unknown error'}`, 'error');
            }
        } catch (err) {
            console.error(err);
            showCustomAlert('Failed to connect to the server. Please try again.', 'error');
        } finally {
            placeOrderBtn.textContent = "Place Order";
            if (cart.length > 0) placeOrderBtn.disabled = false;
        }
    }

    // Initial render
    renderCart();
});
// ===========================================================
