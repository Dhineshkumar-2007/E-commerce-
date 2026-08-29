// ==============================
// SEARCH PRODUCTS
// ==============================

function searchProducts() {

    let search = document.getElementById("searchBox").value.trim();

    if (search === "") {
        alert("Please enter a product name.");
        return;
    }

    fetch("/search?search=" + encodeURIComponent(search))

        .then(response => response.json())

        .then(data => {

            let html = "";

            if (data.length === 0) {

                html = `
                    <h3 style="text-align:center;">
                        No Products Found
                    </h3>
                `;

            } else {

                data.forEach(product => {

                    html += `

                    <div class="product-card">

                        <img
                        src="https://picsum.photos/seed/${product.id}/250/250"
                        >

                        <h3>${product.name}</h3>

                        <p>${product.description}</p>

                        <h2 style="color:green;">
                            ₹${product.mrp}
                        </h2>

                        <form
                        action="/cart/add-to-cart/${product.id}"
                        method="POST">

                            <button
                            class="cart-btn"
                            type="submit">

                                Add To Cart

                            </button>

                        </form>

                    </div>

                    `;

                });

            }

            const resultsEl = document.getElementById("results");
            if (resultsEl) {
                resultsEl.innerHTML = html;
            }
            const searchModal = document.getElementById("searchModal");
            if (searchModal) {
                searchModal.style.display = "block";
            }

        })

        .catch(error => {

            console.log(error);

            alert("Unable to search products.");

        });

}


// ==============================
// CLOSE MODAL
// ==============================

function closeModal() {

    document.getElementById("searchModal").style.display = "none";

}


// ==============================
// CLOSE WHEN CLICKING OUTSIDE
// ==============================

window.onclick = function(event) {

    let modal = document.getElementById("searchModal");

if (modal && event.target === modal) {

        modal.style.display = "none";

    }

}


// ==============================
// SEARCH ON ENTER KEY
// ==============================

const searchBoxEl = document.getElementById("searchBox");
if (searchBoxEl) {
    searchBoxEl.addEventListener("keypress", function(event){

        if(event.key === "Enter"){

            event.preventDefault();

            searchProducts();

        }

    });
}


function addToCart(button) {

        const id = button.dataset.id;

        fetch("/cart/add-to-cart/" + id, {
            method: "POST"
        })
        .then(response => {

            if (response.redirected) {
                window.location.href = response.url;
                return null;
            }

            return response.text();
        })
        .then(data => {

            if (data === null) {
                return;
            }

            if (data === "ok") {
                button.innerText = "✓ Added to Cart";
                button.disabled = true;
                button.style.background = "green";
            }

        })
        .catch(error => {
            console.log(error);
            alert("Unable to add product.");
        });
    }

    document
        .querySelectorAll(".cart-btn[data-id]")
        .forEach(button => {
            button.addEventListener("click", () => addToCart(button));
        });


 // UPDATE UI
        // =========================

        function updateUI() {

            quantitySpan.textContent = quantity;


            const subtotal =
                price * quantity;


            subtotalElement.textContent =
                "₹" + subtotal.toLocaleString("en-IN");


            updateTotal();

        }


