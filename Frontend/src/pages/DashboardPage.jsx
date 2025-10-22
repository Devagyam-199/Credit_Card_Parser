import { Link } from 'react-router-dom';
import TransactionTable from '../components/TransactionTable.jsx';
import SpendingInsights from '../components/SpendingInsights.jsx';
import AIInsights from '../components/AIInsights.jsx';

const DashboardPage = ({ parsedData, onNewUpload }) => {
  const { cardholder_name, card_number, statement_period, payment_due_date, total_amount_due, minimum_amount_due, credit_limit, transactions, transaction_categories, bank_detected } = parsedData || {};

  if (!parsedData) return <Navigate to="/" replace />;

  return (
    <div className="py-4 sm:py-6 lg:py-10 px-2 sm:px-4 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-4 sm:mb-6 flex flex-col sm:flex-row justify-between items-start sm:items-center">
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">Dashboard</h1>
          <Link
            to="/"
            onClick={onNewUpload}
            className="mt-2 sm:mt-0 inline-flex items-center px-3 sm:px-4 py-1 sm:py-2 border border-transparent text-sm sm:text-base font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            New Upload
          </Link>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 mb-6 sm:mb-10">
          <div className="bg-white overflow-hidden shadow rounded-lg p-3 sm:p-4">
            <h3 className="text-sm sm:text-base font-medium text-gray-500">Bank</h3>
            <p className="mt-1 sm:mt-2 text-xl sm:text-2xl font-semibold text-gray-900">{bank_detected || 'Unknown'}</p>
          </div>
          <div className="bg-white overflow-hidden shadow rounded-lg p-3 sm:p-4">
            <h3 className="text-sm sm:text-base font-medium text-gray-500">Cardholder</h3>
            <p className="mt-1 sm:mt-2 text-xl sm:text-2xl font-semibold text-gray-900">{cardholder_name || 'Unknown User'}</p>
          </div>
          <div className="bg-white overflow-hidden shadow rounded-lg p-3 sm:p-4">
            <h3 className="text-sm sm:text-base font-medium text-gray-500">Total Due</h3>
            <p className="mt-1 sm:mt-2 text-xl sm:text-2xl font-semibold text-red-600">₹{total_amount_due || '0.00'}</p>
          </div>
          <div className="bg-white overflow-hidden shadow rounded-lg p-3 sm:p-4">
            <h3 className="text-sm sm:text-base font-medium text-gray-500">Due Date</h3>
            <p className="mt-1 sm:mt-2 text-xl sm:text-2xl font-semibold text-gray-900">{payment_due_date || 'N/A'}</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6 sm:mb-10">
          <SpendingInsights categories={transaction_categories || {}} />
          <AIInsights categories={transaction_categories || {}} totalDue={total_amount_due || '0.00'} transactions={transactions || []} />
        </div>

        <TransactionTable transactions={transactions || []} categories={transaction_categories || {}} />
      </div>
    </div>
  );
};

export default DashboardPage;