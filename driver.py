import asyncio
import time
from catalog import Catalog

async def run_performance_test(num_products=1000, search_term="Product 500", category=None):
    print(f"Starting performance test with {num_products} products...")
    
    # Initialize both systems
    sequential = Catalog()
    asynchronous = Catalog()
    multi_threaded = Catalog()
    
    # Add sample products to both systems
    sample_products = [
        (i, f"Product {i}", "Category A", f"Description for product {i}", 99.99)
        for i in range(num_products)
    ]
    
    print("Adding products to both systems...")
    for prod in sample_products:
        sequential.add_product(*prod)
        asynchronous.add_product(*prod)
        multi_threaded.add_product(*prod)
    
    print(f"\nSearching for '{search_term}' in three systems...")
    
    # Time sequential search
    start_time = time.time()
    sequential_results = await sequential.sequential_search(search_term, category)
    sequential_time = time.time() - start_time
    print(f"Sequential search time: {sequential_time:.3f} seconds")
    print(f"Sequential results found: {len(sequential_results)}")
 
    # Time asyncronous parallel search
    start_time = time.time()
    asynchronous_results = await asynchronous.async_search(search_term, category)
    asynchronous_time = time.time() - start_time
    print(f"Asynchronous parallel search time: {asynchronous_time:.3f} seconds")
    print(f"Asynchronous parallel results found: {len(asynchronous_results)}")
    
    # Time multi-threaded  search
    start_time = time.time()
    multi_threaded_results = await multi_threaded.multi_threaded_search(search_term, category)
    multi_threaded_time = time.time() - start_time
    print(f"Multi-threaded search time: {multi_threaded_time:.3f} seconds")
    print(f"Multi-threaded results found: {len(multi_threaded_results)}")
    
    # Verify results match
    sequential_ids = {p['id'] for p in sequential_results}
    asynchronous_ids = {p['id'] for p in asynchronous_results}
    multi_threaded_ids = {p['id'] for p in multi_threaded_results}

    if sequential_ids != asynchronous_ids or multi_threaded_ids != asynchronous_ids:
        print("\nWARNING: Result sets don't match!")
    else:
        print("\nResults verified: All systems returned identical products")


if __name__ == "__main__":
    # Test with different dataset sizes
    for size in [100, 1000, 10000]:
        print(f"\n{'='*50}")
        asyncio.run(run_performance_test(num_products=size))
