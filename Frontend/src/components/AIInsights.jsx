const AIInsights = ({ categories, totalDue, transactions }) => {
  const totalSpent = Object.values(categories).reduce((sum, val) => sum + (parseFloat(val) || 0), 0);
  const maxCategory = Object.entries(categories).reduce((a, b) => (parseFloat(a[1]) > parseFloat(b[1]) ? a : b))[0];
  const avgDailySpend = transactions.length ? totalSpent / transactions.length : 0;

  const insights = [
    `You spent the most on ${maxCategory || 'N/A'}: ₹${(categories[maxCategory] || 0).toFixed(2)}`,
    `Average daily spend: ₹${avgDailySpend.toFixed(2)}`,
    `Total due this month: ₹${totalDue || '0.00'} (pay at least ₹${parseFloat(categories.minimum_amount_due || 0).toFixed(2)})`,
    `${totalDue ? ((totalSpent / parseFloat(totalDue)) * 100).toFixed(1) : 0}% of your limit utilized this period.`,
  ];

  return (
    <div className="bg-white shadow rounded-lg p-4 sm:p-6 md:p-6">
      <h3 className="text-lg sm:text-xl font-medium text-gray-900 mb-4">Quick Insights</h3>
      <ul className="space-y-2 text-sm sm:text-base text-gray-600">
        {insights.map((insight, idx) => (
          <li key={idx} className="flex items-start">
            <svg className="w-5 h-5 text-green-500 mr-2 mt-0.5 shrink-0" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <span className="wrap-break-word">{insight}</span>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default AIInsights;