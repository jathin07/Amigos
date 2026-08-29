import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute } from './routes/ProtectedRoute';
import Navbar from './components/Navbar';
import Footer from './components/Footer';

// Public pages
import Home from './pages/Home';
import PackagesList from './pages/PackagesList';
import PackageDetail from './pages/PackageDetails';
import BookingForm from './pages/BookingForm';

// Auth Pages & Components
import { 
  LoginPage, 
  ForgotPasswordPage, 
  ResetPasswordPage,
  SessionExpiredModal 
} from './modules/auth';

// Admin Pages & Layout
import { DashboardPage } from './modules/dashboard';
import AdminLayout from './components/layout/AdminLayout';

// CRM Module Pages
import { LeadsPage, LeadDetailPage, CustomersPage } from './modules/crm';

// Proposal Module Pages
import { ProposalListPage, ProposalDetailPage, ProposalBuilderPage } from './modules/proposal';

// Master Data Hub Module Page
import { MasterDataHubPage } from './modules/masters';

// Team & Staff Module Pages
import { TeamListPage, TeamDetailPage } from './modules/team';

// Booking Module Pages
import { BookingListPage, BookingDetailPage } from './modules/booking';

// Finance Module Pages
import { FinanceWorkspacePage } from './modules/finance/pages/FinanceWorkspacePage';

// Vendor Module Pages
import { VendorsPage } from './modules/vendor/pages/VendorsPage';

// Reports Module Pages
import { ReportsPage } from './modules/reports/pages/ReportsPage';

// Organization Module Pages
import { OrganizationPage } from './modules/organization';

// Legacy Pages
import AdminPackages from './pages/AdminPackages';


import './App.css';
import './index.css';

// Initialize TanStack Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 60 * 1000, // 1 minute default
    },
  },
});

function AppContent() {
  const location = useLocation();
  const isAdminRoute = location.pathname.startsWith('/admin');

  return (
    <>
      {/* Conditionally render customer header/footer only for public routes */}
      {!isAdminRoute && <Navbar />}
      
      <Routes>
        {/* Public Customer Routes */}
        <Route path="/" element={<Home />} />
        <Route path="/packages" element={<PackagesList />} />
        <Route path="/packages/:id" element={<PackageDetail />} />
        <Route path="/plan-trip" element={<BookingForm />} />
        
        {/* Admin/Staff Auth Routes */}
        <Route path="/admin/login" element={<LoginPage />} />
        <Route path="/admin/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/admin/reset-password" element={<ResetPasswordPage />} />
        
        {/* Guarded Admin ERP Routes (Wrapped in AdminLayout) */}
        <Route 
          element={
            <ProtectedRoute>
              <AdminLayout />
            </ProtectedRoute>
          }
        >
          <Route path="/admin/dashboard" element={<DashboardPage />} />
          <Route path="/admin/crm/leads" element={<ProtectedRoute permission="crm.read"><LeadsPage /></ProtectedRoute>} />
          <Route path="/admin/crm/leads/:id" element={<ProtectedRoute permission="crm.read"><LeadDetailPage /></ProtectedRoute>} />
          <Route path="/admin/crm/customers" element={<ProtectedRoute permission="crm.contacts.read"><CustomersPage /></ProtectedRoute>} />
          
          <Route path="/admin/proposals" element={<ProtectedRoute permission="proposal.read"><ProposalListPage /></ProtectedRoute>} />
          <Route path="/admin/proposals/:id" element={<ProtectedRoute permission="proposal.read"><ProposalDetailPage /></ProtectedRoute>} />
          <Route path="/admin/proposals/new" element={<ProtectedRoute permission="proposal.write"><ProposalBuilderPage /></ProtectedRoute>} />
          <Route path="/admin/proposals/:id/edit" element={<ProtectedRoute permission="proposal.write"><ProposalBuilderPage /></ProtectedRoute>} />
          
          <Route path="/admin/bookings" element={<ProtectedRoute permission="booking.read"><BookingListPage /></ProtectedRoute>} />
          <Route path="/admin/bookings/:id" element={<ProtectedRoute permission="booking.read"><BookingDetailPage /></ProtectedRoute>} />
          
          <Route path="/admin/masters" element={<ProtectedRoute permission="admin.full"><MasterDataHubPage /></ProtectedRoute>} />
          <Route path="/admin/settings/masters" element={<ProtectedRoute permission="admin.full"><MasterDataHubPage /></ProtectedRoute>} />

          <Route path="/admin/team" element={<ProtectedRoute permission="admin.full"><TeamListPage /></ProtectedRoute>} />
          <Route path="/admin/team/:id" element={<ProtectedRoute permission="admin.full"><TeamDetailPage /></ProtectedRoute>} />
          <Route path="/admin/settings/team" element={<ProtectedRoute permission="admin.full"><TeamListPage /></ProtectedRoute>} />
          <Route path="/admin/settings/organization" element={<ProtectedRoute permission="admin.full"><OrganizationPage /></ProtectedRoute>} />

          {/* Vendors, Finance and Reports Routes */}
          <Route path="/admin/vendors" element={<ProtectedRoute permission="vendor.read"><VendorsPage /></ProtectedRoute>} />
          
          <Route path="/admin/finance/payments" element={<ProtectedRoute permission="finance.read"><FinanceWorkspacePage /></ProtectedRoute>} />
          <Route path="/admin/finance/payouts" element={<ProtectedRoute permission="finance.read"><FinanceWorkspacePage /></ProtectedRoute>} />
          <Route path="/admin/finance/expenses" element={<ProtectedRoute permission="finance.read"><FinanceWorkspacePage /></ProtectedRoute>} />
          <Route path="/admin/finance/profitability" element={<ProtectedRoute permission="finance.read"><FinanceWorkspacePage /></ProtectedRoute>} />
          
          <Route path="/admin/packages" element={<ProtectedRoute permission="package.read"><AdminPackages /></ProtectedRoute>} />
          <Route path="/admin/reports" element={<ProtectedRoute permission="reports.read"><ReportsPage /></ProtectedRoute>} />
        </Route>
      </Routes>
      
      {!isAdminRoute && <Footer />}
    </>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <Router>
          <AppContent />
          {/* Global Session Expired Dialog */}
          <SessionExpiredModal />
        </Router>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
