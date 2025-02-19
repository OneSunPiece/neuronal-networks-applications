import React from 'react';

interface RecommendationItem {
  manufacturer: string;
  name: string;
  ratings: number;
  no_of_ratings: number;
  discount_price: number;
  actual_price: number;
}

interface TableProps {
  data: RecommendationItem[];
}

const columns = [
  { Header: 'Manufacturer', accessor: 'manufacturer' },
  { Header: 'Name', accessor: 'name' },
  { Header: 'Ratings', accessor: 'ratings' },
  { Header: 'Number of Ratings', accessor: 'no_of_ratings' },
  { Header: 'Discount Price', accessor: 'discount_price' },
  { Header: 'Actual Price', accessor: 'actual_price' },
];

const Table: React.FC<TableProps> = ({ data }) => {
  return (
    <table className="min-w-full divide-y divide-gray-200">
      <thead className="bg-gray-50">
        <tr>
          {columns.map((column) => (
            <th
              key={column.accessor}
              scope="col"
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              {column.Header}
            </th>
          ))}
        </tr>
      </thead>
      <tbody className="bg-white divide-y divide-gray-200">
        {data.map((item, index) => (
          <tr key={index}>
            {columns.map((column) => (
              <td key={column.accessor} className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {item[column.accessor as keyof RecommendationItem]}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default Table;