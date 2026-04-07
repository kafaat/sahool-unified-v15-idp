'use client';

import React, { useState, useMemo } from 'react';
import { Package, Plus, Search, AlertTriangle, X } from 'lucide-react';
import { useInventory, useInventoryStats, useUpdateInventory, useCreateInventory } from '@/features/inventory';
import type { InventoryItem, InventoryCategory, InventoryFormData } from '@/features/inventory';

const categories: Array<{ value: InventoryCategory | 'all'; label: string; labelAr: string }> = [
  { value: 'all', label: 'All Categories', labelAr: 'جميع الفئات' },
  { value: 'fertilizers', label: 'Fertilizers', labelAr: 'الأسمدة' },
  { value: 'seeds', label: 'Seeds', labelAr: 'البذور' },
  { value: 'pesticides', label: 'Pesticides', labelAr: 'المبيدات' },
  { value: 'equipment', label: 'Equipment', labelAr: 'المعدات' },
  { value: 'fuel', label: 'Fuel', labelAr: 'الوقود' },
  { value: 'other', label: 'Other', labelAr: 'أخرى' },
];

export default function InventoryClient() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<InventoryCategory | 'all'>('all');
  const [editingItem, setEditingItem] = useState<InventoryItem | null>(null);
  const [editQuantity, setEditQuantity] = useState(0);
  const [editPurchasePrice, setEditPurchasePrice] = useState(0);
  const [editNotes, setEditNotes] = useState('');
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [newName, setNewName] = useState('');
  const [newNameAr, setNewNameAr] = useState('');
  const [newCategory, setNewCategory] = useState<InventoryCategory>('fertilizers');
  const [newQuantity, setNewQuantity] = useState(0);
  const [newUnit, setNewUnit] = useState('');
  const [newUnitAr, setNewUnitAr] = useState('');
  const [newPurchasePrice, setNewPurchasePrice] = useState(0);
  const [newLocation, setNewLocation] = useState('');
  const [newLocationAr, setNewLocationAr] = useState('');

  // Fetch data using React Query hooks
  const {
    data: inventory = [],
    isLoading,
    error,
  } = useInventory(selectedCategory !== 'all' ? { category: selectedCategory } : undefined);
  const { data: stats } = useInventoryStats();
  const updateInventory = useUpdateInventory();
  const createInventory = useCreateInventory();

  const handleOpenEdit = (item: InventoryItem) => {
    setEditingItem(item);
    setEditQuantity(item.quantity);
    setEditPurchasePrice(item.purchasePrice);
    setEditNotes(item.notes ?? '');
  };

  const handleSaveEdit = () => {
    if (!editingItem) return;
    updateInventory.mutate(
      { id: editingItem.id, data: { quantity: editQuantity, purchasePrice: editPurchasePrice, notes: editNotes || undefined } },
      { onSuccess: () => setEditingItem(null) }
    );
  };

  const handleCreate = () => {
    if (!newNameAr) return;
    const data: InventoryFormData = {
      name: newName,
      nameAr: newNameAr,
      category: newCategory,
      sku: '',
      quantity: newQuantity,
      unit: newUnit,
      unitAr: newUnitAr,
      minQuantity: 0,
      purchasePrice: newPurchasePrice,
      location: newLocation || undefined,
      locationAr: newLocationAr || undefined,
    };
    createInventory.mutate(data, {
      onSuccess: () => {
        setShowCreateDialog(false);
        setNewName('');
        setNewNameAr('');
        setNewCategory('fertilizers');
        setNewQuantity(0);
        setNewUnit('');
        setNewUnitAr('');
        setNewPurchasePrice(0);
        setNewLocation('');
        setNewLocationAr('');
      },
    });
  };

  // Filter inventory based on search term
  const filteredInventory = useMemo(() => {
    if (!searchTerm) return inventory;
    const term = searchTerm.toLowerCase();
    return inventory.filter(
      (item) => item.name.toLowerCase().includes(term) || item.nameAr.includes(searchTerm)
    );
  }, [inventory, searchTerm]);

  const getStatusBadge = (status: InventoryItem['status']) => {
    const styles = {
      in_stock: 'bg-green-100 text-green-800',
      low_stock: 'bg-yellow-100 text-yellow-800',
      out_of_stock: 'bg-red-100 text-red-800',
      expired: 'bg-red-100 text-red-800',
    };
    const labels = {
      in_stock: 'متوفر',
      low_stock: 'مخزون منخفض',
      out_of_stock: 'نفذ المخزون',
      expired: 'منتهي الصلاحية',
    };
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${styles[status]}`}>
        {labels[status]}
      </span>
    );
  };

  const lowStockCount = stats?.lowStockItems ?? 0;
  const outOfStockCount = stats?.outOfStockItems ?? 0;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sahool-green-600" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-red-600">فشل في تحميل بيانات المخزون</p>
          <p className="text-gray-500 text-sm">Failed to load inventory data</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Edit Dialog */}
      {editingItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-md p-6 relative">
            <button onClick={() => setEditingItem(null)} className="absolute top-3 left-3 text-gray-400 hover:text-gray-600">
              <X className="w-5 h-5" />
            </button>
            <h2 className="text-lg font-bold text-gray-900 mb-1">تعديل العنصر</h2>
            <p className="text-sm text-gray-500 mb-4">{editingItem.nameAr} ({editingItem.name})</p>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">الكمية ({editingItem.unitAr || editingItem.unit})</label>
                <input type="number" value={editQuantity} onChange={(e) => setEditQuantity(Number(e.target.value))} className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">سعر الشراء (ريال)</label>
                <input type="number" value={editPurchasePrice} onChange={(e) => setEditPurchasePrice(Number(e.target.value))} className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">ملاحظات</label>
                <textarea value={editNotes} onChange={(e) => setEditNotes(e.target.value)} rows={3} className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500" />
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <button onClick={() => setEditingItem(null)} className="px-4 py-2 text-sm text-gray-600 border rounded-lg hover:bg-gray-50">إلغاء</button>
              <button onClick={handleSaveEdit} disabled={updateInventory.isPending} className="px-4 py-2 text-sm text-white bg-sahool-green-600 rounded-lg hover:bg-sahool-green-700 disabled:opacity-50">
                {updateInventory.isPending ? 'جاري الحفظ...' : 'حفظ'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Create Dialog */}
      {showCreateDialog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-md p-6 relative max-h-[90vh] overflow-y-auto">
            <button onClick={() => setShowCreateDialog(false)} className="absolute top-3 left-3 text-gray-400 hover:text-gray-600">
              <X className="w-5 h-5" />
            </button>
            <h2 className="text-lg font-bold text-gray-900 mb-1">إضافة عنصر جديد</h2>
            <p className="text-sm text-gray-500 mb-4">Add New Item</p>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">اسم العنصر (عربي)</label>
                <input type="text" value={newNameAr} onChange={(e) => setNewNameAr(e.target.value)} className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500" placeholder="أدخل الاسم بالعربية" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">اسم العنصر (إنجليزي)</label>
                <input type="text" value={newName} onChange={(e) => setNewName(e.target.value)} className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500" placeholder="Enter name in English" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">الفئة</label>
                <select value={newCategory} onChange={(e) => setNewCategory(e.target.value as InventoryCategory)} className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500">
                  {categories.filter((c) => c.value !== 'all').map((c) => (
                    <option key={c.value} value={c.value}>{c.labelAr}</option>
                  ))}
                </select>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">الكمية</label>
                  <input type="number" value={newQuantity} onChange={(e) => setNewQuantity(Number(e.target.value))} className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">سعر الشراء (ريال)</label>
                  <input type="number" value={newPurchasePrice} onChange={(e) => setNewPurchasePrice(Number(e.target.value))} className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">الوحدة (عربي)</label>
                  <input type="text" value={newUnitAr} onChange={(e) => setNewUnitAr(e.target.value)} className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500" placeholder="كغ" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">الوحدة (إنجليزي)</label>
                  <input type="text" value={newUnit} onChange={(e) => setNewUnit(e.target.value)} className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500" placeholder="kg" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">الموقع (عربي)</label>
                  <input type="text" value={newLocationAr} onChange={(e) => setNewLocationAr(e.target.value)} className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500" placeholder="المستودع الرئيسي" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">الموقع (إنجليزي)</label>
                  <input type="text" value={newLocation} onChange={(e) => setNewLocation(e.target.value)} className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500" placeholder="Main warehouse" />
                </div>
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <button onClick={() => setShowCreateDialog(false)} className="px-4 py-2 text-sm text-gray-600 border rounded-lg hover:bg-gray-50">إلغاء</button>
              <button onClick={handleCreate} disabled={createInventory.isPending || !newNameAr} className="px-4 py-2 text-sm text-white bg-sahool-green-600 rounded-lg hover:bg-sahool-green-700 disabled:opacity-50">
                {createInventory.isPending ? 'جاري الإضافة...' : 'إضافة'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">إدارة المخزون</h1>
          <p className="text-gray-500 mt-1">Inventory Management</p>
        </div>
        <button
          onClick={() => setShowCreateDialog(true)}
          className="inline-flex items-center gap-2 px-4 py-2 bg-sahool-green-600 text-white rounded-lg hover:bg-sahool-green-700 transition-colors"
        >
          <Plus className="w-4 h-4" />
          <span>إضافة عنصر</span>
        </button>
      </div>

      {/* Alerts */}
      {(lowStockCount > 0 || outOfStockCount > 0) && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-amber-600" />
            <span className="font-medium text-amber-800">
              تنبيه المخزون: {lowStockCount} عناصر منخفضة، {outOfStockCount} نفذت
            </span>
          </div>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">إجمالي العناصر</div>
          <div className="text-2xl font-bold text-gray-900">
            {stats?.totalItems ?? inventory.length}
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">القيمة الإجمالية</div>
          <div className="text-2xl font-bold text-green-600">
            {(stats?.totalValue ?? 0).toLocaleString()} ريال
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">مخزون منخفض</div>
          <div className="text-2xl font-bold text-yellow-600">{lowStockCount}</div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">نفذ المخزون</div>
          <div className="text-2xl font-bold text-red-600">{outOfStockCount}</div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="بحث في المخزون..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pr-10 pl-4 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500 focus:border-sahool-green-500"
          />
        </div>
        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value as InventoryCategory | 'all')}
          className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500"
        >
          {categories.map((cat) => (
            <option key={cat.value} value={cat.value}>
              {cat.labelAr}
            </option>
          ))}
        </select>
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">العنصر</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">الفئة</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">الكمية</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">الموقع</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">الحالة</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">
                  الإجراءات
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredInventory.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-gray-500">
                    لا توجد عناصر في المخزون
                  </td>
                </tr>
              ) : (
                filteredInventory.map((item) => (
                  <tr key={item.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-sahool-green-100 rounded-lg flex items-center justify-center">
                          <Package className="w-5 h-5 text-sahool-green-600" />
                        </div>
                        <div>
                          <div className="font-medium text-gray-900">{item.nameAr}</div>
                          <div className="text-sm text-gray-500">{item.name}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {categories.find((c) => c.value === item.category)?.labelAr ?? item.category}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900">
                      {item.quantity} {item.unitAr || item.unit}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {item.locationAr || item.location}
                    </td>
                    <td className="px-4 py-3">{getStatusBadge(item.status)}</td>
                    <td className="px-4 py-3">
                      <button
                        onClick={() => handleOpenEdit(item)}
                        className="text-sahool-green-600 hover:text-sahool-green-700 text-sm font-medium"
                      >
                        تعديل
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
