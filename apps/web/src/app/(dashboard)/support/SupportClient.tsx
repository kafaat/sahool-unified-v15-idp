'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  HelpCircle,
  MessageSquare,
  Phone,
  Mail,
  FileText,
  ChevronDown,
  ChevronUp,
  Send,
  Clock,
  CheckCircle,
  Loader2,
  AlertTriangle,
} from 'lucide-react';
import { supportApi, type Ticket, type CreateTicketRequest } from '@/features/support/api';
import { ApiError } from '@/lib/api/safe-fetch';

interface FAQ {
  id: string;
  question: string;
  questionAr: string;
  answer: string;
  answerAr: string;
  category: string;
}

const faqs: FAQ[] = [
  {
    id: '1',
    question: 'How do I add a new field?',
    questionAr: 'كيف أضيف حقلاً جديداً؟',
    answer:
      "Go to Fields page, click 'Add Field' button, draw the field boundaries on the map, and fill in the field details.",
    answerAr:
      "اذهب إلى صفحة الحقول، انقر على زر 'إضافة حقل'، ارسم حدود الحقل على الخريطة، واملأ تفاصيل الحقل.",
    category: 'fields',
  },
  {
    id: '2',
    question: 'How does the irrigation scheduling work?',
    questionAr: 'كيف تعمل جدولة الري؟',
    answer:
      'The system uses soil moisture sensors, weather data, and crop requirements to automatically suggest optimal irrigation schedules.',
    answerAr:
      'يستخدم النظام حساسات رطوبة التربة وبيانات الطقس ومتطلبات المحصول لاقتراح جداول الري المثلى تلقائياً.',
    category: 'irrigation',
  },
  {
    id: '3',
    question: 'What do the NDVI colors mean?',
    questionAr: 'ماذا تعني ألوان مؤشر NDVI؟',
    answer:
      'Green indicates healthy vegetation, yellow shows moderate health, and red indicates stressed or unhealthy plants.',
    answerAr:
      'اللون الأخضر يشير إلى نباتات صحية، الأصفر يظهر صحة متوسطة، والأحمر يشير إلى نباتات مجهدة أو غير صحية.',
    category: 'satellite',
  },
  {
    id: '4',
    question: 'How do I connect IoT sensors?',
    questionAr: 'كيف أربط حساسات إنترنت الأشياء؟',
    answer:
      "Go to Settings > Devices, click 'Add Sensor', scan the QR code on your sensor, and assign it to a field.",
    answerAr:
      "اذهب إلى الإعدادات > الأجهزة، انقر 'إضافة حساس'، امسح رمز QR على الحساس، وقم بتعيينه لحقل.",
    category: 'iot',
  },
  {
    id: '5',
    question: 'How can I get crop disease diagnosis?',
    questionAr: 'كيف أحصل على تشخيص أمراض المحاصيل؟',
    answer:
      'Take a photo of the affected plant using the mobile app. Our AI will analyze it and provide diagnosis and treatment recommendations.',
    answerAr:
      'التقط صورة للنبات المصاب باستخدام تطبيق الجوال. سيقوم الذكاء الاصطناعي بتحليلها وتقديم التشخيص وتوصيات العلاج.',
    category: 'diseases',
  },
];

export default function SupportClient() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [ticketsLoading, setTicketsLoading] = useState(true);
  const [ticketsError, setTicketsError] = useState<string | null>(null);
  const [expandedFaq, setExpandedFaq] = useState<string | null>(null);
  const [newTicketSubject, setNewTicketSubject] = useState('');
  const [newTicketMessage, setNewTicketMessage] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  const fetchTickets = useCallback(async () => {
    setTicketsLoading(true);
    setTicketsError(null);
    try {
      const data = await supportApi.getTickets();
      setTickets(data);
    } catch (err) {
      const message = err instanceof ApiError ? err.messageAr : 'فشل في جلب التذاكر';
      setTicketsError(message);
    } finally {
      setTicketsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTickets();
  }, [fetchTickets]);

  const handleSubmitTicket = async () => {
    if (!newTicketSubject.trim() || !newTicketMessage.trim()) return;

    setSubmitting(true);
    setSubmitSuccess(false);
    try {
      const newTicket = await supportApi.createTicket({
        subject: newTicketSubject,
        message: newTicketMessage,
      });
      setTickets((prev) => [newTicket, ...prev]);
      setNewTicketSubject('');
      setNewTicketMessage('');
      setSubmitSuccess(true);
      setTimeout(() => setSubmitSuccess(false), 3000);
    } catch (err) {
      const message = err instanceof ApiError ? err.messageAr : 'فشل في إرسال التذكرة';
      alert(message);
    } finally {
      setSubmitting(false);
    }
  };

  const getStatusBadge = (status: Ticket['status']) => {
    const styles = {
      open: 'bg-blue-100 text-blue-800',
      in_progress: 'bg-yellow-100 text-yellow-800',
      resolved: 'bg-green-100 text-green-800',
      closed: 'bg-gray-100 text-gray-800',
    };
    const labels = {
      open: 'مفتوح',
      in_progress: 'قيد المعالجة',
      resolved: 'تم الحل',
      closed: 'مغلق',
    };
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${styles[status]}`}>
        {labels[status]}
      </span>
    );
  };

  const getPriorityBadge = (priority: Ticket['priority']) => {
    const styles = {
      low: 'bg-gray-100 text-gray-800',
      medium: 'bg-yellow-100 text-yellow-800',
      high: 'bg-red-100 text-red-800',
    };
    const labels = {
      low: 'منخفض',
      medium: 'متوسط',
      high: 'عالي',
    };
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${styles[priority]}`}>
        {labels[priority]}
      </span>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">الدعم الفني</h1>
        <p className="text-gray-500 mt-1">Support Center</p>
      </div>

      {/* Contact Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg border p-6 text-center">
          <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Phone className="w-6 h-6 text-blue-600" />
          </div>
          <h3 className="font-semibold text-gray-900 mb-1">اتصل بنا</h3>
          <p className="text-gray-500 text-sm mb-2">Phone Support</p>
          <a href="tel:+966500000000" className="text-sahool-green-600 font-medium">
            +966 50 000 0000
          </a>
        </div>
        <div className="bg-white rounded-lg border p-6 text-center">
          <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <MessageSquare className="w-6 h-6 text-green-600" />
          </div>
          <h3 className="font-semibold text-gray-900 mb-1">محادثة مباشرة</h3>
          <p className="text-gray-500 text-sm mb-2">Live Chat</p>
          <button className="text-sahool-green-600 font-medium">ابدأ محادثة</button>
        </div>
        <div className="bg-white rounded-lg border p-6 text-center">
          <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Mail className="w-6 h-6 text-purple-600" />
          </div>
          <h3 className="font-semibold text-gray-900 mb-1">البريد الإلكتروني</h3>
          <p className="text-gray-500 text-sm mb-2">Email Support</p>
          <a href="mailto:support@sahool.com" className="text-sahool-green-600 font-medium">
            support@sahool.com
          </a>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* FAQs */}
        <div className="bg-white rounded-lg border">
          <div className="p-4 border-b">
            <div className="flex items-center gap-2">
              <HelpCircle className="w-5 h-5 text-sahool-green-600" />
              <h2 className="text-lg font-semibold text-gray-900">الأسئلة الشائعة</h2>
            </div>
          </div>
          <div className="divide-y">
            {faqs.map((faq) => (
              <div key={faq.id}>
                <button
                  onClick={() => setExpandedFaq(expandedFaq === faq.id ? null : faq.id)}
                  className="w-full px-4 py-3 flex items-center justify-between text-right hover:bg-gray-50"
                >
                  <span className="font-medium text-gray-900">{faq.questionAr}</span>
                  {expandedFaq === faq.id ? (
                    <ChevronUp className="w-5 h-5 text-gray-400" />
                  ) : (
                    <ChevronDown className="w-5 h-5 text-gray-400" />
                  )}
                </button>
                {expandedFaq === faq.id && (
                  <div className="px-4 pb-4 text-gray-600 text-sm">{faq.answerAr}</div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Submit Ticket */}
        <div className="bg-white rounded-lg border">
          <div className="p-4 border-b">
            <div className="flex items-center gap-2">
              <FileText className="w-5 h-5 text-sahool-green-600" />
              <h2 className="text-lg font-semibold text-gray-900">إرسال تذكرة دعم</h2>
            </div>
          </div>
          <div className="p-4 space-y-4">
            {submitSuccess && (
              <div className="p-3 bg-green-50 border border-green-200 rounded-lg text-green-700 text-sm">
                تم إرسال التذكرة بنجاح
              </div>
            )}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">الموضوع</label>
              <input
                type="text"
                value={newTicketSubject}
                onChange={(e) => setNewTicketSubject(e.target.value)}
                placeholder="اكتب موضوع المشكلة..."
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">الرسالة</label>
              <textarea
                value={newTicketMessage}
                onChange={(e) => setNewTicketMessage(e.target.value)}
                placeholder="اشرح مشكلتك بالتفصيل..."
                rows={4}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500"
              />
            </div>
            <button
              onClick={handleSubmitTicket}
              disabled={submitting || !newTicketSubject.trim() || !newTicketMessage.trim()}
              className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-sahool-green-600 text-white rounded-lg hover:bg-sahool-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {submitting ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
              <span>{submitting ? 'جاري الإرسال...' : 'إرسال التذكرة'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* My Tickets */}
      <div className="bg-white rounded-lg border">
        <div className="p-4 border-b">
          <h2 className="text-lg font-semibold text-gray-900">تذاكري</h2>
        </div>
        <div className="divide-y">
          {ticketsLoading ? (
            <div className="p-8 text-center">
              <Loader2 className="w-6 h-6 text-sahool-green-600 animate-spin mx-auto mb-2" />
              <p className="text-gray-500 text-sm">جاري تحميل التذاكر...</p>
            </div>
          ) : ticketsError ? (
            <div className="p-8 text-center">
              <AlertTriangle className="w-8 h-8 text-red-400 mx-auto mb-2" />
              <p className="text-gray-500 text-sm mb-2">{ticketsError}</p>
              <button
                onClick={fetchTickets}
                className="text-sahool-green-600 text-sm font-medium hover:underline"
              >
                إعادة المحاولة
              </button>
            </div>
          ) : tickets.length === 0 ? (
            <div className="p-8 text-center text-gray-500">لا توجد تذاكر دعم</div>
          ) : (
            tickets.map((ticket) => (
              <div key={ticket.id} className="p-4 hover:bg-gray-50">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
                      <FileText className="w-5 h-5 text-gray-600" />
                    </div>
                    <div>
                      <div className="font-medium text-gray-900">{ticket.subjectAr}</div>
                      <div className="text-sm text-gray-500">{ticket.id}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {getPriorityBadge(ticket.priority)}
                    {getStatusBadge(ticket.status)}
                  </div>
                </div>
                <div className="mt-2 flex items-center gap-4 text-xs text-gray-400">
                  <span className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    أُنشئت: {new Date(ticket.createdAt).toLocaleDateString('ar-SA')}
                  </span>
                  <span className="flex items-center gap-1">
                    <CheckCircle className="w-3 h-3" />
                    آخر تحديث: {new Date(ticket.updatedAt).toLocaleDateString('ar-SA')}
                  </span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
