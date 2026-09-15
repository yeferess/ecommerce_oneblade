document.addEventListener("DOMContentLoaded", () => {
    const alerta = document.getElementById("alerta");
    const cerrar = document.getElementById("cerrar");

    if (alerta && cerrar) {
        cerrar.addEventListener("click", () => {
            alerta.classList.add("opacity-0");
            setTimeout(() => alerta.remove(), 500);
        });
    }

    document.querySelectorAll('.js-search-form').forEach(initSearchForm);

    function initSearchForm(searchForm) {
        const searchInput = searchForm.querySelector('.js-search-input');
        const searchDropdown = searchForm.querySelector('.js-search-dropdown');
        let searchTimeout;

        if (!searchInput || !searchDropdown) return;

        const searchUrl = searchForm.dataset.searchUrl;

        searchInput.addEventListener('input', function () {
            const query = this.value.trim();
            clearTimeout(searchTimeout);

            if (query.length < 2) {
                searchDropdown.innerHTML = '';
                searchDropdown.classList.add('hidden');
                return;
            }

            searchTimeout = setTimeout(() => {
                fetch(`${searchUrl}?q=${encodeURIComponent(query)}`)
                    .then(response => response.json())
                    .then(data => displayDropdown(data.results, query))
                    .catch(error => console.error('Error:', error));
            }, 300);
        });

        function displayDropdown(products, query) {
            if (products.length === 0) {
                searchDropdown.innerHTML = '<div class="p-4 text-gray-500 text-sm">No se encontraron productos</div>';
                searchDropdown.classList.remove('hidden');
                return;
            }

            searchDropdown.innerHTML = '';

            products.forEach(product => {
                const item = document.createElement('div');
                item.className = 'flex items-center gap-3 p-3 hover:bg-gray-50 cursor-pointer border-b border-gray-100';
                item.innerHTML = `
                    ${product.image_url
                        ? `<img src="${product.image_url}" alt="${escapeHtml(product.name)}" class="w-12 h-12 object-cover rounded">`
                        : '<div class="w-12 h-12 bg-gray-200 rounded"></div>'}
                    <div class="flex-1 min-w-0">
                        <p class="font-semibold text-gray-800 truncate">${escapeHtml(product.name)}</p>
                        <p class="text-sm text-gray-500 truncate">${escapeHtml(product.description)}</p>
                        <p class="text-primary font-bold mt-1">${product.price}</p>
                    </div>`;
                item.addEventListener('click', () => {
                    window.location.href = product.url;
                });
                searchDropdown.appendChild(item);
            });

            const viewAll = document.createElement('div');
            viewAll.className = 'p-3 text-center bg-gray-50 border-t-2 border-gray-200 font-semibold text-primary cursor-pointer hover:bg-gray-100';
            viewAll.textContent = `Ver todos los resultados para "${query}" →`;
            viewAll.addEventListener('click', () => goToSearchResults(query));
            searchDropdown.appendChild(viewAll);

            searchDropdown.classList.remove('hidden');
        }

        function goToSearchResults(query) {
            window.location.href = `${searchForm.action}?q=${encodeURIComponent(query)}`;
        }

        document.addEventListener('click', function (e) {
            if (!searchForm.contains(e.target)) {
                searchDropdown.classList.add('hidden');
            }
        });

        searchForm.addEventListener('submit', function () {
            searchDropdown.classList.add('hidden');
        });
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text || '';
        return div.innerHTML;
    }
});