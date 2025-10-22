import { useState, useEffect } from 'react';

const TransactionTable = ({ transactions, categories }) => {
  const [filterCategory, setFilterCategory] = useState('All');
  const [filterDate, setFilterDate] = useState(''); // Stores yyyy-mm-dd

  // Categorization function mirroring backend logic
  const categorizeTransaction = (description) => {
    const desc = description.toLowerCase();
    if (desc.includes('fuel') || desc.includes('petrol')) return 'Fuel';
    if (desc.includes('zomato') || desc.includes('swiggy') || desc.includes('restaurant')) return 'Food';
    if (desc.includes('flipkart') || desc.includes('amazon')) return 'Shopping';
    if (desc.includes('irctc') || desc.includes('uber')) return 'Travel';
    if (desc.includes('electricity') || desc.includes('airtel') || desc.includes('bill') || desc.includes('payment')) return 'Bills';
    if (desc.includes('netflix') || desc.includes('bookmyshow')) return 'Entertainment';
    return 'Other';
  };

  // Convert transaction date to yyyy-mm-dd format for comparison
  const formatDateForFilter = (dateStr) => {
    if (!dateStr) return '';
    const [day, month, year] = dateStr.split('/');
    return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
  };

  // Filter transactions based on category and date
  const filteredTransactions = transactions.filter((tx) => {
    const cat = categorizeTransaction(tx.description || '');
    const catMatch = filterCategory === 'All' || cat === filterCategory;

    const txDate = formatDateForFilter(tx.date);
    const filterDateObj = filterDate ? new Date(filterDate) : null;
    const txDateObj = txDate ? new Date(txDate) : null;

    const dateMatch = !filterDate || !txDateObj || !filterDateObj || 
      txDateObj.toDateString() === filterDateObj.toDateString();

    return catMatch && dateMatch;
  });

  // Update filterCategory when categories change to ensure valid options
  useEffect(() => {
    if (!['All', ...Object.keys(categories)].includes(filterCategory)) {
      setFilterCategory('All');
    }
  }, [categories, filterCategory]);

  const categoryOptions = ['All', ...Object.keys(categories)].map((cat) => (
    <option key={cat} value={cat}>{cat}</option>
  ));

  return (
    <div className="bg-white shadow rounded-lg">
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-lg font-medium text-gray-900">Transactions</h2>
        <div className="mt-4 flex flex-col sm:flex-row gap-4">
          <select
            value={filterCategory}
            onChange={(e) => setFilterCategory(e.target.value)}
            className="block w-full sm:w-auto px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
          >
            {categoryOptions}
          </select>
          <input
            type="date"
            value={filterDate}
            onChange={(e) => setFilterDate(e.target.value)}
            className="block w-full sm:w-auto px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
          />
        </div>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filteredTransactions.map((tx, idx) => (
              <tr key={idx}>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{tx.date}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 max-w-xs truncate">{tx.description}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                    {categorizeTransaction(tx.description)}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-right">₹{tx.amount} {tx.type ? tx.type : ''}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {filteredTransactions.length === 0 && (
        <div className="px-6 py-4 text-center text-gray-500">No transactions found.</div>
      )}
    </div>
  );
};

export default TransactionTable;