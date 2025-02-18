import { useState, useEffect } from "react";
//import PropTypes from 'prop-types';
//import { sendPredictionRequest } from "../Api/Api";
import "./Recommendations.css";
import { ChevronDownIcon } from '@heroicons/react/16/solid'

export default function Recommendations() {
  const [recommendationsItems, setRecommendationsItems] = useState<string | null>(null);
  const [selectedProduct, setSelectedProduct] = useState<string>("");

  useEffect(() => {
    if (selectedProduct) {
      fetch(`/api/recommendations?product=${selectedProduct}`)
        .then(response => response.json())
        .then(data => setRecommendationsItems(data.recommendations))
        .catch(error => console.error('Error fetching recommendations:', error));
    }
  }, [selectedProduct]);

  const handleProductChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedProduct(event.target.value);
  };

  return (
    <form>
      <div className="space-y-12">
        <div className="border-b border-gray-900/10 pb-12">
          <h2 className="text-base/7 font-semibold text-gray-900">Recommendations</h2>
          <p className="mt-1 text-sm/6 text-gray-600">
            Here you can provide an item you had purchased recently and we will provide you with some recommendations!
          </p>

          <div className="mt-10 grid grid-cols-1 gap-x-6 gap-y-8 sm:grid-cols-6">
            <div className="sm:col-span-3">
              <label htmlFor="recommendation" className="block text-sm/6 font-medium text-gray-900">
                Product
              </label>
              <div className="mt-2 grid grid-cols-1">
                <select 
                  id="product_select"
                  name="product"
                  hx-get="/api/options"
                  hx-trigger="load, keyup delay:300ms"
                  hx-target="#options"
                  className="col-start-1 row-start-1 w-full appearance-none rounded-md bg-white py-1.5 pr-8 pl-3 text-base text-gray-900 outline-1 -outline-offset-1 outline-gray-300 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 sm:text-sm/6"
                  autoComplete="recommendation-name"
                  onChange={handleProductChange}
                >
                  <option value="">Select an option</option>
                  {/* Add options here */}
                </select>
                <ChevronDownIcon
                  aria-hidden="true"
                  className="pointer-events-none col-start-1 row-start-1 mr-2 size-5 self-center justify-self-end text-gray-500 sm:size-4"
                />
              </div>
            </div>
          </div>
        </div>

        <div className="border-b border-gray-900/10 pb-12">
          <h2 className="text-base/7 font-semibold text-gray-900">Recommended</h2>
          <p className="mt-1 text-sm/6 text-gray-600">
            {recommendationsItems ? 
              <p>recommended: {recommendationsItems}</p> : <p>Please provide an item you had purchased recently</p>
            }
          </p>
        </div>
      </div>

      <div className="mt-6 flex items-center justify-end gap-x-6">
        <button type="button" className="text-sm/6 font-semibold text-gray-900">
          Cancel
        </button>
        <button
          type="submit"
          className="rounded-md bg-teal-600 px-3 py-2 text-sm font-semibold text-white shadow-xs hover:bg-teal-500 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-600"
        >
          Send
        </button>
      </div>
    </form>
  )
}