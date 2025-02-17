import { useState } from "react";
import "./TimeSeries.css";
import { ChevronDownIcon } from '@heroicons/react/16/solid'
import TimeSeriesChart from "../components/TimeSeriesChart/TimeSeriesChart";

interface DataPoint {
  date: string;
  value: number;
}

export default function TimeSeries() {
  const [predictions, setPredictions] = useState<DataPoint[] | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isPredicted, setIsPredicted] = useState<boolean>(false);
  const [selectedTienda, setSelectedTienda] = useState<string>("");
  const [selectedDepartamento, setSelectedDepartamento] = useState<string>("");

  const tiendas = [
    { name: 'Tienda 1'},
    { name: 'Tienda 2'},
    { name: 'Tienda 3'}
  ];
  const departamentos = [
    { name: 'Departamento 1'},
    { name: 'Departamento 2'},
    { name: 'Departamento 3'}
  ];

  const timeSeriesDummyData: DataPoint[] = Array.from({ length: 60 }, (_, i) => ({
    date: new Date(2025, 0, 10 + i).toISOString().split("T")[0],
    value: Math.floor(Math.random() * (250 - 120 + 1)) + 120,
  }));
  

  const TimeSeriesRequest = async (selectedTienda: string, selectedDepartamento: string) => {
    const data = { selectedTienda, selectedDepartamento };

    const response = await fetch(`/api/time-series`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });
    const result = await response.json();
    return result;
  }

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsLoading(true); // Set loading to true before the request is sent

    if (!selectedTienda || !selectedDepartamento) {
      alert("Please select a tienda and a departamento first.");
      setIsLoading(false);
      return;
    }

    try {
      const result = await TimeSeriesRequest(selectedTienda, selectedDepartamento);
      const predictionData: DataPoint[] = result.prediction.map((value: string, index: number) => ({ x: index + 1, y: value }));
      setPredictions(predictionData);
      setIsPredicted(true);
    } catch (error) {
      setIsPredicted(true); // @TODO: REMOVE THIS LINE
      console.error('Error sending prediction request:', error);
    } finally {
      // Set loading to false after the request is completed
      setIsLoading(false); 
    }
  };

  return (
    <form onSubmit={handleSubmit} className="form-time-series">
      <div className="space-y-12">

        <div className="border-b border-gray-900/10 pb-12">
          <h2 className="text-base/7 font-semibold text-gray-900">Time Series</h2>
          <p className="mt-1 text-sm/6 text-gray-600">
            Select the time series you want to analyze.
          </p>
          {isLoading ? <h2>Loading...</h2> : null}
        </div>

        <div className="border-b border-gray-900/10 pb-12">

          <div className="mt-10 grid grid-cols-1 gap-x-6 gap-y-8 sm:grid-cols-6">
            <div className="sm:col-span-3">
              <label htmlFor="departamento" className="block text-sm/6 font-medium text-gray-900">
                Departamento
              </label>
              <div className="mt-2 grid grid-cols-1">
                <select 
                  id="departamento_select"
                  name="departamento"
                  className="col-start-1 row-start-1 w-full appearance-none rounded-md bg-white py-1.5 pr-8 pl-3 text-base text-gray-900 outline-1 -outline-offset-1 outline-gray-300 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 sm:text-sm/6"
                  autoComplete="country-name"
                  value={selectedDepartamento}
                  onChange={(e) => setSelectedDepartamento(e.target.value)}
                >
                  <option value="">Select an option</option>
                  {departamentos.map((departamento) => (
                    <option key={departamento.name} value={departamento.name}>{departamento.name}</option>
                  ))}
                </select>
                <ChevronDownIcon
                  aria-hidden="true"
                  className="pointer-events-none col-start-1 row-start-1 mr-2 size-5 self-center justify-self-end text-gray-500 sm:size-4"
                />
              </div>
            </div>
          </div>

          <div className="mt-10 grid grid-cols-1 gap-x-6 gap-y-8 sm:grid-cols-6">
            <div className="sm:col-span-3">
              <label htmlFor="tienda" className="block text-sm/6 font-medium text-gray-900">
                Tienda
              </label>
              <div className="mt-2 grid grid-cols-1">
                <select 
                  id="tienda_select"
                  name="tienda"
                  className="col-start-1 row-start-1 w-full appearance-none rounded-md bg-white py-1.5 pr-8 pl-3 text-base text-gray-900 outline-1 -outline-offset-1 outline-gray-300 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 sm:text-sm/6"
                  autoComplete="country-name"
                  value={selectedTienda}
                  onChange={(e) => setSelectedTienda(e.target.value)}
                >
                  <option value="">Select an option</option>
                  {tiendas.map((item) => (
                    <option key={item.name} value={item.name}>{item.name}</option>
                  ))}
                </select>
                <ChevronDownIcon
                  aria-hidden="true"
                  className="pointer-events-none col-start-1 row-start-1 mr-2 size-5 self-center justify-self-end text-gray-500 sm:size-4"
                />
              </div>
            </div>
          </div>

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
      { predictions ? null : null } {/* @TODO: REMOVE THIS*/}
      { isPredicted ? <TimeSeriesChart data={timeSeriesDummyData}/> : null }
    </form>
  )
}