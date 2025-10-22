import { PieChart, Pie, Cell, ResponsiveContainer, Legend } from 'recharts';

const SpendingInsights = ({ categories }) => {
  // Convert categories to data format, handle N/A or invalid values with 0
  const data = Object.entries(categories).map(([name, value]) => ({
    name,
    value: parseFloat(value) || 0, // Default to 0 if value is invalid or "N/A"
  })).filter(item => item.value > 0); // Filter out zero values to avoid clutter

  // Define a consistent color palette
  const COLORS = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEEAD', '#D4A5A5', '#9B59B6'];

  // Calculate total for percentage calculation
  const total = data.reduce((sum, entry) => sum + entry.value, 0);

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Spending by Category</h3>
      {data.length > 0 ? (
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              outerRadius={100}
              fill="#8884d8"
              dataKey="value"
              labelLine={false}
              label={({ name, value, cx, cy, midAngle }) => {
                const RADIAN = Math.PI / 180;
                const radius = 100 + 10;
                const x = cx + radius * Math.cos(-midAngle * RADIAN);
                const y = cy + radius * Math.sin(-midAngle * RADIAN);
                const percentage = ((value / total) * 100).toFixed(1);
                return (
                  <text
                    x={x}
                    y={y}
                    fill="#333"
                    textAnchor={x > cx ? 'start' : 'end'}
                    dominantBaseline="central"
                  >
                    {`${name} (${percentage}%)`}
                  </text>
                );
              }}
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Legend
              layout="vertical"
              verticalAlign="bottom"
              align="center"
              wrapperStyle={{ paddingTop: '20px' }}
            />
          </PieChart>
        </ResponsiveContainer>
      ) : (
        <p className="text-center text-gray-500">No spending data available.</p>
      )}
      <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
        {data.map((entry, idx) => (
          <div key={entry.name} className="flex items-center">
            <div className="w-4 h-4 rounded-full mr-2" style={{ backgroundColor: COLORS[idx % COLORS.length] }}></div>
            <span className="text-gray-700">{entry.name}:</span>
            <span className="ml-auto font-medium text-gray-900">₹{entry.value.toFixed(2)}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SpendingInsights;