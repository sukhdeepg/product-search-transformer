document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('search-form');
    const searchQuery = document.getElementById('search-query');
    const searchResults = document.getElementById('search-results');
    const loadingIndicator = document.getElementById('loading');
    
    // Check model status on page load
    checkModelStatus();
    
    // Function to check if the model is loaded
    async function checkModelStatus() {
        try {
            searchForm.classList.add('disabled');
            searchQuery.disabled = true;
            loadingIndicator.classList.remove('d-none');
            
            searchResults.innerHTML = `
                <div class="alert alert-info">
                    <h4>Loading model...</h4>
                    <p>The sentence transformer model is being loaded. This may take a few moments.</p>
                </div>
            `;
            
            const response = await fetch('/status');
            const data = await response.json();
            
            if (data.model_loaded && data.embeddings_loaded) {
                // Model is ready
                searchForm.classList.remove('disabled');
                searchQuery.disabled = false;
                loadingIndicator.classList.add('d-none');
                searchResults.innerHTML = `
                    <div class="alert alert-success">
                        <h4>Ready!</h4>
                        <p>The model is loaded and ready for your search queries.</p>
                    </div>
                `;
            } else {
                // Model is still loading
                setTimeout(checkModelStatus, 2000); // Check again in 2 seconds
            }
        } catch (error) {
            console.error('Error checking model status:', error);
            searchResults.innerHTML = `
                <div class="alert alert-warning">
                    <h4>Loading model...</h4>
                    <p>Still waiting for the model to load. This may take a minute or two.</p>
                </div>
            `;
            setTimeout(checkModelStatus, 3000); // Try again in 3 seconds
        }
    }

    searchForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const query = searchQuery.value.trim();
        if (!query) return;

        // Show loading indicator
        loadingIndicator.classList.remove('d-none');
        searchResults.innerHTML = '';
        
        try {
            // Create form data for the POST request
            const formData = new FormData();
            formData.append('query', query);
            
            // Send the search request
            const response = await fetch('/search', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                // Handle error responses with error messages
                const errorMessage = data.error || 'Search request failed';
                throw new Error(errorMessage);
            }
            
            displayResults(data.results, query);
        } catch (error) {
            console.error('Error during search:', error);
            searchResults.innerHTML = `
                <div class="alert alert-danger">
                    <h4>Error</h4>
                    <p>${error.message || 'An error occurred during search. Please try again.'}</p>
                </div>
            `;
        } finally {
            // Hide loading indicator
            loadingIndicator.classList.add('d-none');
        }
    });

    function displayResults(results, query) {
        if (!results || results.length === 0) {
            searchResults.innerHTML = `
                <div class="no-results">
                    <h4>No matching products found</h4>
                    <p>Try a different search term or browse our categories</p>
                </div>
            `;
            return;
        }
        
        // Group results by category
        const resultsByCategory = {};
        results.forEach(product => {
            const category = product.category || 'Other';
            if (!resultsByCategory[category]) {
                resultsByCategory[category] = [];
            }
            resultsByCategory[category].push(product);
        });
        
        let resultsHtml = `
            <h3>Search Results for "${escapeHtml(query)}"</h3>
            <p class="search-tip">Showing ${results.length} product(s) ranked by relevance</p>
        `;
        
        // Display results by category
        for (const [category, categoryProducts] of Object.entries(resultsByCategory)) {
            resultsHtml += `
                <div class="category-section mb-4">
                    <h4 class="category-heading">${category} <span class="badge bg-secondary">${categoryProducts.length}</span></h4>
                    <div class="row">
            `;
            
            categoryProducts.forEach(product => {
                // Determine score class based on match quality
                let scoreClass = '';
                if (product.score >= 80) {
                    scoreClass = 'score-high';
                } else if (product.score >= 50) {
                    scoreClass = 'score-medium';
                } else {
                    scoreClass = 'score-low';
                }
                
                resultsHtml += `
                    <div class="col-md-6 col-lg-4 mb-3">
                        <div class="card product-card ${scoreClass} h-100">
                            <div class="card-header bg-light d-flex justify-content-between align-items-center">
                                <h5 class="card-title mb-0">${product.name}</h5>
                                <span class="badge bg-primary score-badge">${product.score}% match</span>
                            </div>
                            <div class="card-body">
                                <p class="card-text">${product.description}</p>
                                <div class="text-end">
                                    <span class="badge bg-light text-dark">ID: ${product.id}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            });
            
            resultsHtml += '</div></div>';
        }
        
        searchResults.innerHTML = resultsHtml;
    }
    
    // Helper function to escape HTML
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
});
