import React, { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { 
  useBookingDetail, 
  useConfirmBooking, 
  useCancelBooking, 
  useBookingTravelers,
  useAddTraveler,
  useUpdateTraveler,
  useDeleteTraveler,
  useUpdateBooking,
  useUpdateBookingStatus,
  useBookingDocuments,
  useAddDocument,
  useDeleteDocument
} from "../hooks/useBooking";

import BookingStatusBadge from "../components/BookingStatusBadge";
import BookingOverviewTab from "../components/BookingOverviewTab";
import PaymentScheduleTab from "../components/PaymentScheduleTab";
import BookingTimeline from "../components/BookingTimeline";

// Modals and Drawers
import ConfirmBookingModal from "../modals/ConfirmBookingModal";
import CancelBookingModal from "../modals/CancelBookingModal";
import AddEditTravelerDrawer from "../drawers/AddEditTravelerDrawer";
import EditBookingDrawer from "../drawers/EditBookingDrawer";

import { 
  Luggage, 
  Calendar, 
  ArrowLeft, 
  Loader2, 
  CheckCircle2, 
  XCircle, 
  Users, 
  FileText, 
  Clock, 
  AlertCircle,
  Plus,
  Trash2,
  Edit2,
  FileSpreadsheet,
  Download,
  DollarSign
} from "lucide-react";

export function BookingDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState("overview");

  // State for modles/drawers
  const [isConfirmOpen, setIsConfirmOpen] = useState(false);
  const [isCancelOpen, setIsCancelOpen] = useState(false);
  const [isEditBookingOpen, setIsEditBookingOpen] = useState(false);
  const [isTravelerDrawerOpen, setIsTravelerDrawerOpen] = useState(false);
  const [selectedTraveler, setSelectedTraveler] = useState(null);

  // Document add form state
  const [docFormData, setDocFormData] = useState({
    file_name: "",
    file_url: "",
    document_type: "PASSPORT"
  });

  // Queries
  const { data: bookingResponse, isLoading, isError, refetch: refetchDetail } = useBookingDetail(id);
  const { data: travelersResponse } = useBookingTravelers(id);
  const { data: documentsResponse } = useBookingDocuments(id);

  // Mutations
  const confirmMutation = useConfirmBooking(id);
  const cancelMutation = useCancelBooking(id);
  const updateBookingMutation = useUpdateBooking(id);
  const updateStatusMutation = useUpdateBookingStatus(id);
  const addTravelerMutation = useAddTraveler(id);
  const updateTravelerMutation = useUpdateTraveler(id);
  const deleteTravelerMutation = useDeleteTraveler(id);
  const addDocumentMutation = useAddDocument(id);
  const deleteDocumentMutation = useDeleteDocument(id);

  const booking = bookingResponse?.data;
  const travelers = travelersResponse?.data || booking?.travelers || [];
  const documents = documentsResponse?.data || booking?.documents || [];

  // Handlers
  const handleStatusTransition = (targetStatusCode, notes) => {
    updateStatusMutation.mutate({ status_code: targetStatusCode, notes }, {
      onSuccess: () => {
        refetchDetail();
      }
    });
  };
  const handleConfirmSubmit = (payload) => {
    confirmMutation.mutate(payload, {
      onSuccess: () => {
        setIsConfirmOpen(false);
        refetchDetail();
      }
    });
  };

  const handleCancelSubmit = (payload) => {
    cancelMutation.mutate(payload, {
      onSuccess: () => {
        setIsCancelOpen(false);
        refetchDetail();
      }
    });
  };

  const handleUpdateBookingSubmit = (payload) => {
    updateBookingMutation.mutate(payload, {
      onSuccess: () => {
        setIsEditBookingOpen(false);
        refetchDetail();
      }
    });
  };

  const handleTravelerSubmit = (payload) => {
    if (selectedTraveler) {
      updateTravelerMutation.mutate(payload, {
        onSuccess: () => {
          setIsTravelerDrawerOpen(false);
          setSelectedTraveler(null);
        }
      });
    } else {
      addTravelerMutation.mutate(payload, {
        onSuccess: () => {
          setIsTravelerDrawerOpen(false);
        }
      });
    }
  };

  const handleDeleteTraveler = (travelerId) => {
    if (window.confirm("Are you sure you want to remove this traveler from the manifest?")) {
      deleteTravelerMutation.mutate(travelerId);
    }
  };

  const handleDocChange = (key, val) => {
    setDocFormData(prev => ({ ...prev, [key]: val }));
  };

  const handleAddDocument = (e) => {
    e.preventDefault();
    if (!docFormData.file_name.trim() || !docFormData.file_url.trim()) {
      alert("Please fill in file name and URL.");
      return;
    }
    addDocumentMutation.mutate(docFormData, {
      onSuccess: () => {
        setDocFormData({
          file_name: "",
          file_url: "",
          document_type: "PASSPORT"
        });
      }
    });
  };

  const handleDeleteDocument = (docId) => {
    if (window.confirm("Are you sure you want to delete this document?")) {
      deleteDocumentMutation.mutate(docId);
    }
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-3">
        <Loader2 className="animate-spin text-blue-600" size={24} />
        <p className="text-xs font-semibold text-slate-500">Loading booking file workspace...</p>
      </div>
    );
  }

  if (isError || !booking) {
    return (
      <div className="bg-white border border-slate-200 rounded-2xl p-12 text-center space-y-4 max-w-lg mx-auto mt-8">
        <AlertCircle className="mx-auto text-rose-500" size={32} />
        <h2 className="text-lg font-bold text-slate-800">Booking File Not Found</h2>
        <p className="text-xs text-slate-500">The requested booking workspace file does not exist or has been archived.</p>
        <button
          onClick={() => navigate("/admin/bookings")}
          className="px-4 py-2 bg-slate-800 text-white rounded-lg text-xs font-bold hover:bg-slate-900"
        >
          Back to Bookings Registry
        </button>
      </div>
    );
  }

  // Lifecycle check
  const statusCode = booking.status?.code || "";
  const isWaitingForAdvance = statusCode === "WAITING_FOR_ADVANCE";
  const isTerminal = ["CANCELLED", "COMPLETED", "CLOSED"].includes(statusCode);

  return (
    <div className="space-y-6 flex flex-col h-full select-none">
      
      {/* 1. Header Navigation */}
      <div className="flex items-center space-x-3">
        <button
          onClick={() => navigate("/admin/bookings")}
          className="p-1.5 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 transition-colors"
        >
          <ArrowLeft size={16} />
        </button>
        <div className="text-xs font-semibold text-slate-400 flex items-center space-x-1">
          <span>Bookings Registry</span>
          <span>/</span>
          <span className="text-slate-700 font-bold">{booking.booking_number}</span>
        </div>
      </div>

      {/* 2. Banner Header */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-6">
        <div className="space-y-1">
          <div className="flex items-center space-x-3">
            <h1 className="text-xl font-bold text-slate-800 tracking-tight">
              {booking.booking_number}
            </h1>
            <BookingStatusBadge status={booking.status} />
          </div>
          <p className="text-xs font-semibold text-slate-500">
            Primary Client: <span className="text-slate-800 font-bold">{booking.snapshots?.contact_person_name || "Client File"}</span>
            {booking.group_name && (
              <span className="ml-2 px-1.5 py-0.5 rounded bg-slate-100 text-slate-600 border border-slate-200 font-mono text-[9px]">
                {booking.group_name}
              </span>
            )}
          </p>
        </div>

        {/* Status Actions */}
        <div className="flex items-center space-x-3 shrink-0 flex-wrap gap-2">
          {!isTerminal && (
            <button
              onClick={() => setIsEditBookingOpen(true)}
              className="flex items-center space-x-1.5 px-3.5 py-2 border border-slate-200 hover:bg-slate-50 text-slate-700 rounded-lg text-xs font-bold transition-colors"
            >
              <Edit2 size={14} />
              <span>Edit Details</span>
            </button>
          )}

          {isWaitingForAdvance && (
            <button
              onClick={() => setIsConfirmOpen(true)}
              className="flex items-center space-x-1.5 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-bold shadow-sm transition-colors"
            >
              <CheckCircle2 size={14} />
              <span>Confirm Booking</span>
            </button>
          )}

          {statusCode === "CONFIRMED" && (
            <button
              onClick={() => handleStatusTransition("PLANNING", "Moved file to operations planning.")}
              disabled={updateStatusMutation.isPending}
              className="flex items-center space-x-1.5 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-bold shadow-sm transition-colors"
            >
              {updateStatusMutation.isPending ? <Loader2 className="animate-spin" size={14} /> : <CheckCircle2 size={14} />}
              <span>Move to Planning</span>
            </button>
          )}

          {statusCode === "PLANNING" && (
            <button
              onClick={() => handleStatusTransition("READY", "Marked trip ready for departure.")}
              disabled={updateStatusMutation.isPending}
              className="flex items-center space-x-1.5 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-bold shadow-sm transition-colors"
            >
              {updateStatusMutation.isPending ? <Loader2 className="animate-spin" size={14} /> : <CheckCircle2 size={14} />}
              <span>Mark Trip Ready</span>
            </button>
          )}

          {statusCode === "READY" && (
            <button
              onClick={() => handleStatusTransition("ONGOING", "Trip execution started.")}
              disabled={updateStatusMutation.isPending}
              className="flex items-center space-x-1.5 px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg text-xs font-bold shadow-sm transition-colors"
            >
              {updateStatusMutation.isPending ? <Loader2 className="animate-spin" size={14} /> : <CheckCircle2 size={14} />}
              <span>Start Trip (Ongoing)</span>
            </button>
          )}

          {statusCode === "ONGOING" && (
            <button
              onClick={() => handleStatusTransition("COMPLETED", "Trip successfully completed.")}
              disabled={updateStatusMutation.isPending}
              className="flex items-center space-x-1.5 px-4 py-2 bg-teal-600 hover:bg-teal-700 text-white rounded-lg text-xs font-bold shadow-sm transition-colors"
            >
              {updateStatusMutation.isPending ? <Loader2 className="animate-spin" size={14} /> : <CheckCircle2 size={14} />}
              <span>Complete Trip</span>
            </button>
          )}

          {statusCode === "COMPLETED" && (
            <button
              onClick={() => handleStatusTransition("CLOSED", "File closed and archived.")}
              disabled={updateStatusMutation.isPending}
              className="flex items-center space-x-1.5 px-4 py-2 bg-slate-800 hover:bg-slate-900 text-white rounded-lg text-xs font-bold shadow-sm transition-colors"
            >
              {updateStatusMutation.isPending ? <Loader2 className="animate-spin" size={14} /> : <CheckCircle2 size={14} />}
              <span>Close File</span>
            </button>
          )}

          {!isTerminal && (
            <button
              onClick={() => setIsCancelOpen(true)}
              className="flex items-center space-x-1.5 px-4 py-2 border border-rose-200 hover:bg-rose-50 text-rose-600 rounded-lg text-xs font-bold transition-colors"
            >
              <XCircle size={14} />
              <span>Cancel File</span>
            </button>
          )}
        </div>
      </div>

      {/* 3. Navigation Tabs */}
      <div className="flex border-b border-slate-200 bg-white rounded-xl overflow-hidden shadow-xs border">
        {[
          { id: "overview", label: "File Overview", icon: FileText },
          { id: "travelers", label: "Traveler Manifest", icon: Users },
          { id: "schedule", label: "Payment Schedule", icon: DollarSign },
          { id: "documents", label: "Documents Vault", icon: Luggage },
          { id: "timeline", label: "Audit Timeline", icon: Clock },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-1 flex items-center justify-center space-x-2 py-3 px-4 border-b-2 text-xs font-bold transition-all focus:outline-none ${
                isActive
                  ? "border-blue-600 text-blue-600 bg-blue-50/30"
                  : "border-transparent text-slate-500 hover:text-slate-800 hover:bg-slate-50"
              }`}
            >
              <Icon size={16} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* 4. Tab Content */}
      <div className="flex-1">
        
        {/* OVERVIEW */}
        {activeTab === "overview" && (
          <BookingOverviewTab 
            booking={booking} 
            onEditClick={() => setIsEditBookingOpen(true)} 
          />
        )}

        {/* TRAVELERS */}
        {activeTab === "travelers" && (
          <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">Passenger Roster & Govt ID Info</h3>
                <p className="text-[10px] text-slate-400 font-semibold mt-0.5">Exactly one traveler must be designated as group leader</p>
              </div>
              {!isTerminal && (
                <button
                  onClick={() => {
                    setSelectedTraveler(null);
                    setIsTravelerDrawerOpen(true);
                  }}
                  className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold rounded-lg flex items-center space-x-1"
                >
                  <Plus size={14} />
                  <span>Add Passenger</span>
                </button>
              )}
            </div>

            {travelers.length === 0 ? (
              <div className="text-center py-8 text-slate-400 text-xs font-semibold">
                No passenger roster details registered yet.
              </div>
            ) : (
              <div className="space-y-2.5">
                {travelers.map((t) => (
                  <div key={t.id} className="p-4 border border-slate-200 rounded-xl flex items-center justify-between text-xs bg-slate-50/30 hover:bg-slate-50 transition-colors">
                    <div className="space-y-1">
                      <span className="font-bold text-slate-800 flex items-center">
                        {t.name}
                        {t.is_group_leader && (
                          <span className="ml-2 px-1.5 py-0.5 rounded text-[8px] font-extrabold uppercase bg-emerald-50 border border-emerald-100 text-emerald-700">
                            Lead Traveler
                          </span>
                        )}
                      </span>
                      <span className="text-[10px] text-slate-400 block font-semibold">
                        {t.age ? `${t.age} yrs` : "Age TBD"} • {t.gender || "Gender TBD"} 
                        {t.id_proof_type && ` • ID: ${t.id_proof_type} (${t.id_proof_number})`}
                      </span>
                      {t.special_requirements && (
                        <p className="text-[10px] text-amber-700 font-semibold mt-1">
                          Reqs: {t.special_requirements}
                        </p>
                      )}
                    </div>

                    {!isTerminal && (
                      <div className="flex items-center space-x-1.5">
                        <button
                          onClick={() => {
                            setSelectedTraveler(t);
                            setIsTravelerDrawerOpen(true);
                          }}
                          className="p-1 rounded-lg border border-slate-200 text-slate-500 hover:text-blue-600 hover:bg-white transition-colors"
                          title="Edit Details"
                        >
                          <Edit2 size={13} />
                        </button>
                        {!t.is_group_leader && (
                          <button
                            onClick={() => handleDeleteTraveler(t.id)}
                            className="p-1 rounded-lg border border-slate-200 text-slate-500 hover:text-rose-600 hover:bg-white transition-colors"
                            title="Remove Traveler"
                          >
                            <Trash2 size={13} />
                          </button>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* PAYMENT SCHEDULE */}
        {activeTab === "schedule" && (
          <PaymentScheduleTab booking={booking} />
        )}

        {/* DOCUMENTS */}
        {activeTab === "documents" && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* List Documents */}
            <div className="lg:col-span-2 bg-white border border-slate-200 rounded-xl p-6 shadow-sm space-y-4">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 border-b border-slate-100 pb-3">
                Uploaded Booking Vouchers & Flight Tickets
              </h3>

              {documents.length === 0 ? (
                <div className="text-center py-10 text-slate-400 text-xs font-semibold">
                  No documents attached to this booking workspace file yet.
                </div>
              ) : (
                <div className="space-y-2">
                  {documents.map((doc) => (
                    <div key={doc.id} className="p-3 border border-slate-200 rounded-xl flex items-center justify-between text-xs bg-slate-50/30 hover:bg-slate-50">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 rounded-lg bg-blue-50 border border-blue-100 flex items-center justify-center text-blue-600 shrink-0">
                          <FileSpreadsheet size={16} />
                        </div>
                        <div>
                          <span className="font-bold text-slate-800 block">{doc.file_name}</span>
                          <span className="text-[10px] text-slate-400 font-semibold">
                            Type: {doc.document_type?.name || "General"} • Uploaded: {new Date(doc.uploaded_at).toLocaleDateString("en-IN")}
                          </span>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <a
                          href={doc.file_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="p-1.5 rounded-lg border border-slate-200 text-slate-500 hover:text-blue-600 hover:bg-white transition-colors"
                          title="Open/Download Link"
                        >
                          <Download size={13} />
                        </a>
                        {!isTerminal && (
                          <button
                            onClick={() => handleDeleteDocument(doc.id)}
                            className="p-1.5 rounded-lg border border-slate-200 text-slate-500 hover:text-rose-600 hover:bg-white transition-colors"
                            title="Delete file"
                          >
                            <Trash2 size={13} />
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Document upload form panel */}
            {!isTerminal && (
              <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-4 h-fit">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 border-b border-slate-100 pb-2">
                  Attach Voucher Link
                </h4>
                <form onSubmit={handleAddDocument} className="space-y-3.5">
                  <div>
                    <label className="block text-[10px] font-bold text-slate-600 uppercase mb-1">Document Label *</label>
                    <input
                      type="text"
                      required
                      placeholder="e.g. Flight ticket PDF"
                      value={docFormData.file_name}
                      onChange={(e) => handleDocChange("file_name", e.target.value)}
                      className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500 font-semibold"
                    />
                  </div>

                  <div>
                    <label className="block text-[10px] font-bold text-slate-600 uppercase mb-1">Document URL *</label>
                    <input
                      type="url"
                      required
                      placeholder="https://drive.google.com/..."
                      value={docFormData.file_url}
                      onChange={(e) => handleDocChange("file_url", e.target.value)}
                      className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500 font-semibold"
                    />
                  </div>

                  <div>
                    <label className="block text-[10px] font-bold text-slate-600 uppercase mb-1">Document Type</label>
                    <select
                      value={docFormData.document_type}
                      onChange={(e) => handleDocChange("document_type", e.target.value)}
                      className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500 font-semibold"
                    >
                      <option value="PASSPORT">Passport copy</option>
                      <option value="TICKET">Flight/Train ticket</option>
                      <option value="VOUCHER">Hotel voucher</option>
                      <option value="VISA">Visa proof</option>
                      <option value="OTHER">Other attachment</option>
                    </select>
                  </div>

                  <button
                    type="submit"
                    disabled={addDocumentMutation.isPending}
                    className="w-full py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-bold flex items-center justify-center space-x-1.5 shadow-sm"
                  >
                    {addDocumentMutation.isPending && <Loader2 className="animate-spin" size={12} />}
                    <span>Register Link</span>
                  </button>
                </form>
              </div>
            )}

          </div>
        )}

        {/* TIMELINE */}
        {activeTab === "timeline" && (
          <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 border-b border-slate-100 pb-3 mb-4">
              Booking Activity Audit Trail
            </h3>
            <BookingTimeline bookingId={booking.id} />
          </div>
        )}

      </div>

      {/* MODALS & DRAWERS WIRING */}
      <ConfirmBookingModal
        isOpen={isConfirmOpen}
        onClose={() => setIsConfirmOpen(false)}
        onConfirm={handleConfirmSubmit}
        isPending={confirmMutation.isPending}
        rowVersion={booking.row_version}
        bookingNumber={booking.booking_number}
        totalAmount={booking.total_amount}
      />

      <CancelBookingModal
        isOpen={isCancelOpen}
        onClose={() => setIsCancelOpen(false)}
        onCancel={handleCancelSubmit}
        isPending={cancelMutation.isPending}
        rowVersion={booking.row_version}
        bookingNumber={booking.booking_number}
      />

      <AddEditTravelerDrawer
        isOpen={isTravelerDrawerOpen}
        onClose={() => {
          setIsTravelerDrawerOpen(false);
          setSelectedTraveler(null);
        }}
        onSubmit={handleTravelerSubmit}
        isPending={addTravelerMutation.isPending || updateTravelerMutation.isPending}
        traveler={selectedTraveler}
      />

      <EditBookingDrawer
        isOpen={isEditBookingOpen}
        onClose={() => setIsEditBookingOpen(false)}
        onSubmit={handleUpdateBookingSubmit}
        isPending={updateBookingMutation.isPending}
        booking={booking}
      />

    </div>
  );
}

export default BookingDetailPage;
