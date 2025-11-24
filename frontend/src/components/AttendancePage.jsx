import { useState, useEffect } from 'react';
import { Camera, CheckCircle, Download, Calendar } from 'lucide-react';
import { Sidebar } from './Sidebar';
import { Navbar } from './Navbar';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';






export function AttendancePage({ user, onNavigate, onLogout }) {
  const [isRecognizing, setIsRecognizing] = useState(false);
  const [recognizedUser, setRecognizedUser] = useState(null);
  const [filterDate, setFilterDate] = useState('');
  const [todayRecord, setTodayRecord] = useState(null);
  const [loadingToday, setLoadingToday] = useState(true);

  const mockAttendanceRecords = [
    { id: 1, name: 'John Doe', userId: 'EMP001', status: 'Present', timestamp: '2024-11-14 09:15 AM', department: 'Engineering' },
    { id: 2, name: 'Jane Smith', userId: 'EMP002', status: 'Present', timestamp: '2024-11-14 09:18 AM', department: 'Marketing' },
    { id: 3, name: 'Mike Johnson', userId: 'EMP003', status: 'Present', timestamp: '2024-11-14 09:22 AM', department: 'Sales' },
    { id: 4, name: 'Sarah Williams', userId: 'EMP004', status: 'Present', timestamp: '2024-11-14 09:25 AM', department: 'HR' },
    { id: 5, name: 'Tom Brown', userId: 'EMP005', status: 'Present', timestamp: '2024-11-14 09:30 AM', department: 'Engineering' },
    { id: 6, name: 'Emily Davis', userId: 'EMP006', status: 'Absent', timestamp: '-', department: 'Marketing' },
  ];

  const handleStartRecognition = () => {
    setIsRecognizing(true);
    // In this simplified flow we'll call the face recognition endpoint if available
    (async () => {
      try {
        const { apiFetch } = await import('../api');
        // This example assumes you have an image input or camera capture; here we just call mark endpoint
        const res = await apiFetch('/api/attendance/mark', { method: 'POST', body: JSON.stringify({}) });
        setRecognizedUser({ name: user.name, id: user.id, status: res.get ? 'Present' : 'Present', timestamp: new Date().toLocaleString() });
      } catch (err) {
        console.error(err);
      } finally {
        setIsRecognizing(false);
      }
    })();
  };

  // Load today's attendance on mount
  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const { apiFetch } = await import('../api');
        const data = await apiFetch('/api/attendance/today');
        if (mounted) {
          setTodayRecord(data.record || data.summary || null);
        }
      } catch (err) {
        console.error('Failed to load today attendance', err);
      } finally {
        setLoadingToday(false);
      }
    })();
    return () => { mounted = false; };
  }, []);

  const handleExportCSV = () => {
    // Mock CSV export
    console.log('Exporting attendance records to CSV...');
  };

  const handleExportPDF = () => {
    // Mock PDF export
    console.log('Exporting attendance records to PDF...');
  };

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar currentPage="attendance" onNavigate={onNavigate} userRole={user.role} />
      <div className="flex-1 flex flex-col">
        <Navbar user={user} onLogout={onLogout} />
        <main className="flex-1 p-6">
          <div className="mb-6">
            <h1 className="text-gray-900 mb-2">Attendance Records</h1>
            <p className="text-gray-600">
              Mark your attendance using face recognition or view attendance history
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
            {/* Face Recognition */}
            <Card className="lg:col-span-1 p-6">
              <h2 className="text-gray-900 mb-4">Mark Attendance</h2>
              <div className="aspect-square bg-gray-900 rounded-lg mb-4 flex items-center justify-center relative overflow-hidden">
                {!isRecognizing && !recognizedUser && (
                  <div className="text-center">
                    <Camera className="w-16 h-16 text-gray-600 mx-auto mb-2" />
                    <p className="text-gray-400">Click below to start</p>
                  </div>
                )}
                {isRecognizing && (
                  <div className="w-full h-full bg-gradient-to-br from-blue-900 to-blue-700 flex items-center justify-center">
                    <div className="text-center">
                      <div className="w-32 h-32 border-4 border-blue-400 rounded-full flex items-center justify-center mb-4 animate-pulse">
                        <Camera className="w-16 h-16 text-blue-200" />
                      </div>
                      <p className="text-white">Recognizing...</p>
                    </div>
                  </div>
                )}
                {recognizedUser && (
                  <div className="w-full h-full bg-gradient-to-br from-green-900 to-green-700 flex items-center justify-center">
                    <div className="text-center text-white">
                      <CheckCircle className="w-20 h-20 mx-auto mb-4" />
                      <p className="mb-1">Success!</p>
                    </div>
                  </div>
                )}
              </div>

              <Button
                onClick={handleStartRecognition}
                disabled={isRecognizing}
                className="w-full bg-blue-600 hover:bg-blue-700 mb-3"
              >
                <Camera className="w-5 h-5 mr-2" />
                {isRecognizing ? 'Recognizing...' : 'Start Recognition'}
              </Button>

              {recognizedUser && (
                <Card className="p-4 bg-green-50 border-green-200">
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Name:</span>
                      <span className="text-gray-900">{recognizedUser.name}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">ID:</span>
                      <span className="text-gray-900">{recognizedUser.id}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Status:</span>
                      <span className="text-green-600">{recognizedUser.status}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Time:</span>
                      <span className="text-gray-900">{recognizedUser.timestamp}</span>
                    </div>
                  </div>
                </Card>
              )}
            </Card>

            {/* Attendance History */}
            <Card className="lg:col-span-2 p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-gray-900">Today's Attendance</h2>
                <div className="flex gap-2">
                  <Button onClick={handleExportCSV} variant="outline" size="sm">
                    <Download className="w-4 h-4 mr-2" />
                    CSV
                  </Button>
                  <Button onClick={handleExportPDF} variant="outline" size="sm">
                    <Download className="w-4 h-4 mr-2" />
                    PDF
                  </Button>
                </div>
              </div>

              <div className="mb-4">
                <Label htmlFor="filter-date">Filter by Date</Label>
                <div className="flex gap-2 mt-2">
                  <div className="relative flex-1">
                    <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                    <Input
                      id="filter-date"
                      type="date"
                      value={filterDate}
                      onChange={(e) => setFilterDate(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                  <Button variant="outline">Apply</Button>
                </div>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-gray-200">
                      <th className="text-left py-3 px-4 text-gray-600">User ID</th>
                      <th className="text-left py-3 px-4 text-gray-600">Name</th>
                      <th className="text-left py-3 px-4 text-gray-600">Department</th>
                      <th className="text-left py-3 px-4 text-gray-600">Timestamp</th>
                      <th className="text-left py-3 px-4 text-gray-600">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {mockAttendanceRecords.map((record) => (
                      <tr key={record.id} className="border-b border-gray-100">
                        <td className="py-3 px-4 text-gray-900">{record.userId}</td>
                        <td className="py-3 px-4 text-gray-900">{record.name}</td>
                        <td className="py-3 px-4 text-gray-600">{record.department}</td>
                        <td className="py-3 px-4 text-gray-600">{record.timestamp}</td>
                        <td className="py-3 px-4">
                          <span
                            className={`inline-flex items-center px-3 py-1 rounded-full ${record.status === 'Present'
                              ? 'bg-green-100 text-green-800'
                              : 'bg-red-100 text-red-800'
                              }`}
                          >
                            {record.status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          </div>
        </main>
      </div>
    </div>
  );
}


