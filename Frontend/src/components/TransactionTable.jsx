import { useState, useEffect } from 'react';

const TransactionTable = ({ transactions, categories }) => {
  const [filterCategory, setFilterCategory] = useState('All');
  const [filterDate, setFilterDate] = useState('');

  const categorizeTransaction = (description, amount, type) => {
    const desc = description.toLowerCase().replace(/[^a-z0-9 ]/g, ' ');
    const amountNum = parseFloat(amount.replace(/[^0-9.]/g, '')) || 0;
    const isDebit = !type || type.toUpperCase() !== 'CR';

    if (!isDebit) return 'Other';

    if (['fuel', 'petrol', 'diesel', 'hpcl', 'ioc', 'indianoil', 'bharat petroleum', 'shell', 'pump'].some(word => desc.includes(word))) return 'Fuel';
    if (['food', 'zomato', 'swiggy', 'restaurant', 'cafe', 'dominos', 'pizza', 'mcdonald', 'kfc', 'burger', 'dining'].some(word => desc.includes(word))) return 'Food';
    if (['flipkart', 'amazon', 'myntra', 'ajio', 'meesho', 'store', 'shopping', 'bigbasket', 'reliance digital', 'rel retail', 'digital', 'retail', 'mall'].some(word => desc.includes(word))) return 'Shopping';
    if (['makemytrip', 'ixigo', 'irctc', 'goibibo', 'uber', 'ola', 'rapido', 'flight', 'hotel', 'booking', 'bus', 'train'].some(word => desc.includes(word))) return 'Travel';
    if (['electricity', 'water', 'gas', 'broadband', 'mobile', 'recharge', 'postpaid', 'dth', 'billdesk', 'bill payment', 'airtel', 'jio', 'upi', 'neft', 'imps', 'payment', 'transfer'].some(word => desc.includes(word))) return 'Bills';
    if (['netflix', 'hotstar', 'prime video', 'spotify', 'bookmyshow', 'movie', 'game', 'youtube', 'pvr', 'inox'].some(word => desc.includes(word))) return 'Entertainment';
    return 'Other';
  };

  const formatDateForFilter = (dateStr) => {
    if (!dateStr) return '';
    const [day, month, year] = dateStr.split('/');
    return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
  };

  const filteredTransactions = transactions.filter((tx) => {
    const cat = categorizeTransaction(tx.description || '', tx.amount || '0', tx.type || '');
    const catMatch = filterCategory === 'All' || cat === filterCategory;

    const txDate = formatDateForFilter(tx.date);
    const filterDateObj = filterDate ? new Date(filterDate) : null;
    const txDateObj = txDate ? new Date(txDate) : null;

    const dateMatch = !filterDate || !txDateObj || !filterDateObj || 
      txDateObj.toDateString() === filterDateObj.toDateString();

    return catMatch && dateMatch;
  });

  useEffect(() => {
    if (!['All', ...Object.keys(categories)].includes(filterCategory)) {
      setFilterCategory('All');
    }
  }, [categories, filterCategory]);

  const categoryOptions = ['All', ...Object.keys(categories)].map((cat) => (
    <option key={cat} value={cat} className="text-sm sm:text-base">
      {cat}
    </option>
  ));

  return (
    <div className="bg-white shadow rounded-lg p-4 sm:p-6">
      <div className="px-0 sm:px-6 py-2 sm:py-4 border-b border-gray-200">
        <h2 className="text-lg sm:text-xl font-medium text-gray-900">Transactions</h2>
        <div className="mt-2 sm:mt-4 flex flex-col sm:flex-row gap-2 sm:gap-4">
          <select
            value={filterCategory}
            onChange={(e) => setFilterCategory(e.target.value)}
            className="block w-full sm:w-auto px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-sm sm:text-base"
          >
            {categoryOptions}
          </select>
          <input
            type="date"
            value={filterDate}
            onChange={(e) => setFilterDate(e.target.value)}
            className="block w-full sm:w-auto px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-sm sm:text-base"
          />
        </div>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-2 sm:px-6 py-2 sm:py-3 text-left text-xs sm:text-sm font-medium text-gray-500 uppercase tracking-wider">Date</th>
              <th className="px-2 sm:px-6 py-2 sm:py-3 text-left text-xs sm:text-sm font-medium text-gray-500 uppercase tracking-wider">Description</th>
              <th className="px-2 sm:px-6 py-2 sm:py-3 text-left text-xs sm:text-sm font-medium text-gray-500 uppercase tracking-wider">Category</th>
              <th className="px-2 sm:px-6 py-2 sm:py-3 text-right text-xs sm:text-sm font-medium text-gray-500 uppercase tracking-wider">Amount</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filteredTransactions.map((tx, idx) => (
              <tr key={idx}>
                <td className="px-2 sm:px-6 py-2 sm:py-4 whitespace-nowrap text-sm text-gray-900">{tx.date}</td>
                <td className="px-2 sm:px-6 py-2 sm:py-4 whitespace-nowrap text-sm text-gray-900 max-w-xs sm:max-w-sm truncate">{tx.description}</td>
                <td className="px-2 sm:px-6 py-2 sm:py-4 whitespace-nowrap text-sm text-gray-500">
                  <span className="inline-flex px-1 sm:px-2 py-0.5 sm:py-1 text-xs sm:text-sm font-semibold rounded-full bg-blue-100 text-blue-800">
                    {categorizeTransaction(tx.description, tx.amount, tx.type)}
                  </span>
                </td>
                <td className="px-2 sm:px-6 py-2 sm:py-4 whitespace-nowrap text-sm text-gray-900 text-right">₹{tx.amount} {tx.type ? tx.type : ''}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {filteredTransactions.length === 0 && (
        <div className="px-2 sm:px-6 py-4 text-center text-gray-500 text-sm sm:text-base">No transactions found.</div>
      )}
    </div>
  );
};

export default TransactionTable;