from typing import List, Dict
import time
import asyncio
from collections import defaultdict
import concurrent.futures
import concurrent
from timing import SEARCH_LOOKUP_TIME
from timing import PRODUCT_LOOKUP_TIME
from timing import CATEGORY_LOOKUP_TIME

class Catalog:
    def __init__(self):
        # Simulating a large in-memory database
        self.products = {}
        self.categories = defaultdict(list)
        self.search_terms = defaultdict(list)
        
    def add_product(self, product_id: int, name: str, category: str, description: str, price: float):
        """Add a product to the catalog"""
        product = {
            'id': product_id,
            'name': name,
            'category': category,
            'description': description,
            'price': price
        }
        self.products[product_id] = product
        self.categories[category].append(product_id)
        
        # Index search terms
        terms = f"{name} {description}".lower().split()
        for term in terms:
            self.search_terms[term].append(product_id)

    async def get_product_details(self, product_id: int) -> Dict:
        """Get detailed information about a specific product"""
        await asyncio.sleep(PRODUCT_LOOKUP_TIME)
        return self.products.get(product_id)

    async def get_search_results(self, query: str) -> List[int]:
        await asyncio.sleep(SEARCH_LOOKUP_TIME)
        query_terms = query.lower().split()
        matching_ids = set()
        for term in query_terms:
            matching_ids.update(self.search_terms.get(term, []))
        return matching_ids

    async def get_category_products(self, category: str) -> List[int]:
        """Get product IDs for a category"""
        await asyncio.sleep(CATEGORY_LOOKUP_TIME)
        return self.categories.get(category, [])

    async def get_matching_ids(self, query: str, category: str = None) -> List[int]:
        matching_ids = await self.get_search_results(query)
        # Apply category filter if specified
        if category:
            category_ids = set(await self.get_category_products(category))
            matching_ids = matching_ids.intersection(category_ids)
        return matching_ids

    async def sequential_search(self, query: str, category: str = None) -> List[Dict]:
        """Search products by query string and optional category"""
        matching_ids = await self.get_matching_ids(query, category)
        
        # Retrieve matching products sequentially 
        results = []
        for product_id in matching_ids:
            results.append(await self.get_product_details(product_id))
    
        return results

    async def async_search(self, query: str, category: str = None) -> List[Dict]:
        matching_ids = await self.get_matching_ids(query, category)
        
        # Retrieve all matching products in parallel
        product_tasks = [
            self.get_product_details(pid) 
            for pid in matching_ids
        ]
        
        # Gather all product results
        products = await asyncio.gather(*product_tasks)
        return products
    
    async def multi_threaded_search(self, query: str, category: str = None) -> List[Dict]:
        matching_ids = await self.get_matching_ids(query, category)
        products = self.fetch_products_threads(matching_ids)
        return products



    def fetch_products_threads(self, matching_ids):
        max_workers = 50  # Adjust as needed
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            product_tasks = {executor.submit(run_async_in_thread, self.get_product_details, pid): pid for pid in matching_ids}
            products = [future.result() for future in concurrent.futures.as_completed(product_tasks)]
        return products  

# helper function allowing us to run async get_product_details in a separate thread
def run_async_in_thread(async_func, *args):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(async_func(*args))
    loop.close()
    return result        

