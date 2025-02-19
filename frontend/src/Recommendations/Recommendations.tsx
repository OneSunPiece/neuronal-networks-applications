import { useState } from "react";
//import PropTypes from 'prop-types';
//import { sendPredictionRequest } from "../Api/Api";
import "./Recommendations.css";
import  Table from "../components/Table/Table";
import { ChevronDownIcon } from '@heroicons/react/16/solid'

export default function Recommendations() {
  interface RecommendationItem {
    manufacturer: string;
    name: string;
    ratings: number;
    no_of_ratings: number;
    discount_price: number;
    actual_price: number;
  }
  
  const [recommendationsItems, setRecommendationsItems] = useState<RecommendationItem[]>([]);
  const [selectedProduct, setSelectedProduct] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isPredicted, setIsPredicted] = useState<boolean>(false);

  const clientes = [
    { id:1, name: "Camilo", lastPurchase: "Solimo Laundry Basket with Lid, 55 Litres, Silver" },
    { id:2, name: "Sofia", lastPurchase: "1 Ton 4 Star Fixed Speed Window AC (Copper, Turbo Cool, Dust Filter, 2022 Model, White)" },
    { id:3, name: "Jose", lastPurchase: "Premium 750 Watt Mixer Grinder with 3 Stainless Steel Jar + 1 Juicer Jar, Black & Grey" },
    { id:4, name: "Mariana", lastPurchase: "- Solimo PVC Front Load Fully Automatic Washing Machine Cover, Polka, Blue" },
    { id:5, name: "Ronaldo", lastPurchase: "Sport Men Sweatshirt" },
    { id:6, name: "Juan Carlos", lastPurchase: "6-Feet DisplayPort (not USB port) to HDMI Cable Black" },
    { id:7, name: "Simon", lastPurchase: "polyester 23 Cms Gym Bag(7572229_Pink_X_Red)" },
    { id:8, name: "Juan Pablo", lastPurchase: "Men's Contaro M Flip Flop & Slipper" },
    { id:9, name: "Valentina", lastPurchase: "- Eden & Ivy Women's Cotton Knee Length Casual Regular Nightgown" },
    { id:10, name: "Daniela", lastPurchase: "Men's Maxico Running Shoes" }
  ]

  const RecommendationRequest = async (lastPurchase: string) => {
    const URL = "https://2lm3d3is4idywwxyin37wc2mxm0oaypf.lambda-url.us-east-1.on.aws/";
    const body_format = {
    data: lastPurchase
    };

    console.log("Sending request to:", URL);
    console.log("Data:", body_format);
    const response = await fetch(URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body_format),
    });
    console.log("Request sent.");

    const result = await response.json();
    console.log("Response:", result);
    return result;
  }

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsPredicted(false);
    setIsLoading(true); // Set loading to true before the request is sent

    if (!selectedProduct) {
      alert("Please select a Client to recommended items based on their last purchase.");
      setIsLoading(false);
      return;
    }

    try {
      const result = await RecommendationRequest(selectedProduct);
      setRecommendationsItems(result);
      //setPredictions(predictionData);
      setIsPredicted(true);
    } catch (error) {
      console.error('Error sending prediction request:', error);
      setIsLoading(false); 
    } finally {
      // Set loading to false after the request is completed
      setIsLoading(false); 
    }
  };

  const handleProductChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedProduct(event.target.value);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-12">
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
                  {clientes.map((cliente) => (
                    <option key={cliente.id} value={cliente.lastPurchase}>
                      {cliente.name}: {cliente.lastPurchase}
                    </option>
                  ))}
                </select>
                <ChevronDownIcon
                  aria-hidden="true"
                  className="pointer-events-none col-start-1 row-start-1 mr-2 size-5 self-center justify-self-end text-gray-500 sm:size-4"
                />
              </div>
            </div>
          </div>
          <small className="block mt-8 text-sm/6 text-gray-500">
                (Prediction in real time, based on last purchased items, with some register users.)
          </small>
        </div>

        <div className="border-b border-gray-900/10 pb-12">
          <h2 className="text-base/7 font-semibold text-gray-900">Recommended</h2>
            {isLoading ? <p className="mt-1 text-sm/6 text-gray-600">Loading...</p>: null}
            {isPredicted ? 
              //<p>asd</p>
              <Table data={recommendationsItems}/>
              : 
              <p>Please provide an item you had purchased recently</p>
            }
        </div>
      </div>

      <div className="mt-6 flex items-center justify-end gap-x-6">
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