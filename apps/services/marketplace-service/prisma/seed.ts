/**
 * SAHOOL Marketplace Service - Database Seeding
 * خدمة السوق - بذر قاعدة البيانات
 *
 * This script populates the database with sample marketplace data for development and testing.
 * هذا السكريبت يملأ قاعدة البيانات ببيانات سوق عينة للتطوير والاختبار.
 *
 * Usage: npx prisma db seed
 */

import {
  PrismaClient,
  ProductCategory,
  SellerType,
  ProductStatus,
  OrderStatus,
  PaymentStatus,
  CreditTier,
  LoanPurpose,
  LoanStatus,
  BusinessType,
} from '@prisma/client';

const prisma = new PrismaClient();

// Sample governorates (Yemen)
// المحافظات العينة (اليمن)
const GOVERNORATES = ['صنعاء', 'عدن', 'تعز', 'الحديدة', 'إب', 'ذمار'];

// Sample products data
// بيانات المنتجات العينة
const PRODUCT_TEMPLATES = [
  // Harvests - المحاصيل
  {
    name: 'Organic Wheat',
    nameAr: 'قمح عضوي',
    category: ProductCategory.HARVEST,
    unit: 'ton',
    basePrice: 150000,
  },
  {
    name: 'Premium Barley',
    nameAr: 'شعير ممتاز',
    category: ProductCategory.HARVEST,
    unit: 'ton',
    basePrice: 120000,
  },
  {
    name: 'Fresh Tomatoes',
    nameAr: 'طماطم طازجة',
    category: ProductCategory.HARVEST,
    unit: 'kg',
    basePrice: 500,
  },
  {
    name: 'Medjool Dates',
    nameAr: 'تمر مجدول',
    category: ProductCategory.HARVEST,
    unit: 'kg',
    basePrice: 2500,
  },
  // Seeds - البذور
  {
    name: 'Wheat Seeds (Certified)',
    nameAr: 'بذور قمح (معتمدة)',
    category: ProductCategory.SEEDS,
    unit: 'kg',
    basePrice: 800,
  },
  {
    name: 'Tomato Seeds (Hybrid)',
    nameAr: 'بذور طماطم (هجين)',
    category: ProductCategory.SEEDS,
    unit: 'unit',
    basePrice: 50,
  },
  // Fertilizers - الأسمدة
  {
    name: 'Urea 46%',
    nameAr: 'يوريا 46%',
    category: ProductCategory.FERTILIZER,
    unit: 'kg',
    basePrice: 200,
  },
  {
    name: 'NPK 20-20-20',
    nameAr: 'NPK 20-20-20',
    category: ProductCategory.FERTILIZER,
    unit: 'kg',
    basePrice: 350,
  },
  // Pesticides - المبيدات
  {
    name: 'Organic Neem Oil',
    nameAr: 'زيت النيم العضوي',
    category: ProductCategory.PESTICIDE,
    unit: 'unit',
    basePrice: 1500,
  },
  // Equipment - المعدات
  {
    name: 'Drip Irrigation Kit',
    nameAr: 'طقم الري بالتنقيط',
    category: ProductCategory.IRRIGATION,
    unit: 'unit',
    basePrice: 25000,
  },
];

/**
 * Create sample seller profiles
 * إنشاء ملفات بائعين عينة
 */
async function createSellers(count: number) {
  const sellers = [];
  const businessTypes = [
    BusinessType.INDIVIDUAL,
    BusinessType.FARM,
    BusinessType.COOPERATIVE,
    BusinessType.DISTRIBUTOR,
  ];

  for (let i = 0; i < count; i++) {
    const seller = await prisma.sellerProfile.create({
      data: {
        userId: `seller-${String(i + 1).padStart(3, '0')}`,
        tenantId: 'tenant-demo-001',
        businessName: `Farm ${String.fromCharCode(65 + i)} Agricultural`,
        businessType: businessTypes[i % businessTypes.length],
        rating: parseFloat((3.5 + Math.random() * 1.5).toFixed(1)),
        totalSales: Math.floor(Math.random() * 100),
        totalRevenue: Math.floor(Math.random() * 10000000),
        verified: i < 3, // First 3 are verified
        verifiedAt: i < 3 ? new Date() : null,
        bankAccount: {
          bankName: 'Yemen Bank',
          accountNumber: `****${String(1000 + i).slice(-4)}`,
          iban: `YE00${String(1000000 + i)}`,
        },
      },
    });
    sellers.push(seller);
  }

  return sellers;
}

/**
 * Create sample buyer profiles
 * إنشاء ملفات مشترين عينة
 */
async function createBuyers(count: number) {
  const buyers = [];

  for (let i = 0; i < count; i++) {
    const governorate = GOVERNORATES[i % GOVERNORATES.length];
    const buyer = await prisma.buyerProfile.create({
      data: {
        userId: `buyer-${String(i + 1).padStart(3, '0')}`,
        tenantId: 'tenant-demo-001',
        shippingAddresses: [
          {
            label: 'Home',
            governorate,
            district: `District ${i + 1}`,
            street: `Street ${i + 1}`,
            phone: `+9677${String(70000000 + i).slice(-8)}`,
            isDefault: true,
          },
        ],
        preferredPayment: ['wallet', 'cash', 'bank_transfer'][i % 3],
        totalPurchases: Math.floor(Math.random() * 50),
        totalSpent: Math.floor(Math.random() * 5000000),
        loyaltyPoints: Math.floor(Math.random() * 1000),
      },
    });
    buyers.push(buyer);
  }

  return buyers;
}

/**
 * Create sample wallets
 * إنشاء محافظ عينة
 */
async function createWallets(sellerIds: string[], buyerIds: string[]) {
  const wallets = [];
  const creditTiers = [CreditTier.BRONZE, CreditTier.SILVER, CreditTier.GOLD, CreditTier.PLATINUM];

  // Create wallets for sellers
  for (const sellerId of sellerIds) {
    const wallet = await prisma.wallet.create({
      data: {
        userId: sellerId,
        userType: 'farmer',
        balance: Math.floor(Math.random() * 1000000),
        escrowBalance: Math.floor(Math.random() * 100000),
        currency: 'YER',
        creditScore: 300 + Math.floor(Math.random() * 550),
        creditTier: creditTiers[Math.floor(Math.random() * creditTiers.length)],
        loanLimit: Math.floor(Math.random() * 5000000),
        currentLoan: 0,
        isVerified: true,
        kycStatus: 'approved',
      },
    });
    wallets.push(wallet);
  }

  // Create wallets for buyers
  for (const buyerId of buyerIds) {
    const wallet = await prisma.wallet.create({
      data: {
        userId: buyerId,
        userType: 'buyer',
        balance: Math.floor(Math.random() * 500000),
        escrowBalance: 0,
        currency: 'YER',
        creditScore: 300 + Math.floor(Math.random() * 350),
        creditTier: creditTiers[Math.floor(Math.random() * 3)], // Buyers typically lower tier
        loanLimit: Math.floor(Math.random() * 1000000),
        currentLoan: 0,
        isVerified: Math.random() > 0.5,
        kycStatus: Math.random() > 0.5 ? 'approved' : 'pending',
      },
    });
    wallets.push(wallet);
  }

  return wallets;
}

/**
 * Create sample products
 * إنشاء منتجات عينة
 */
async function createProducts(sellers: { userId: string }[]) {
  const products = [];

  for (const seller of sellers) {
    // Each seller has 3-6 products
    const productCount = Math.floor(Math.random() * 4) + 3;
    const templates = [...PRODUCT_TEMPLATES].sort(() => Math.random() - 0.5).slice(0, productCount);

    for (const template of templates) {
      const governorate = GOVERNORATES[Math.floor(Math.random() * GOVERNORATES.length)];
      const priceVariation = 0.8 + Math.random() * 0.4; // 80% - 120% of base price

      const product = await prisma.product.create({
        data: {
          name: template.name,
          nameAr: template.nameAr,
          category: template.category,
          price: Math.floor(template.basePrice * priceVariation),
          stock: Math.floor(Math.random() * 100) + 10,
          unit: template.unit,
          description: `High quality ${template.name.toLowerCase()} from local farms.`,
          descriptionAr: `${template.nameAr} عالي الجودة من المزارع المحلية.`,
          sellerId: seller.userId,
          sellerType: SellerType.FARMER,
          governorate,
          district: `District ${Math.floor(Math.random() * 10) + 1}`,
          cropType: template.category === ProductCategory.HARVEST ? template.name.split(' ')[0].toLowerCase() : null,
          harvestDate: template.category === ProductCategory.HARVEST
            ? new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000)
            : null,
          qualityGrade: ['A', 'B', 'C'][Math.floor(Math.random() * 3)],
          status: ProductStatus.AVAILABLE,
          featured: Math.random() > 0.8, // 20% are featured
        },
      });
      products.push(product);
    }
  }

  return products;
}

/**
 * Create sample orders
 * إنشاء طلبات عينة
 */
async function createOrders(
  products: { id: string; price: number; sellerId: string }[],
  buyers: { userId: string }[]
) {
  const orders = [];
  const statuses = [OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.DELIVERED, OrderStatus.CANCELLED];

  for (let i = 0; i < 20; i++) {
    const buyer = buyers[Math.floor(Math.random() * buyers.length)];
    const itemCount = Math.floor(Math.random() * 3) + 1;
    const selectedProducts = [...products].sort(() => Math.random() - 0.5).slice(0, itemCount);

    let subtotal = 0;
    const items = selectedProducts.map(product => {
      const quantity = Math.floor(Math.random() * 5) + 1;
      const totalPrice = product.price * quantity;
      subtotal += totalPrice;
      return {
        productId: product.id,
        quantity,
        unitPrice: product.price,
        totalPrice,
      };
    });

    const deliveryFee = Math.floor(Math.random() * 5000) + 1000;
    const serviceFee = Math.floor(subtotal * 0.02); // 2% service fee
    const status = statuses[Math.floor(Math.random() * statuses.length)];

    const order = await prisma.order.create({
      data: {
        orderNumber: `ORD-${Date.now()}-${String(i + 1).padStart(4, '0')}`,
        buyerId: buyer.userId,
        buyerName: `Buyer ${i + 1}`,
        buyerPhone: `+9677${String(70000000 + i).slice(-8)}`,
        subtotal,
        deliveryFee,
        serviceFee,
        totalAmount: subtotal + deliveryFee + serviceFee,
        status,
        paymentStatus: status === OrderStatus.DELIVERED ? PaymentStatus.PAID : PaymentStatus.UNPAID,
        paymentMethod: ['wallet', 'cash'][Math.floor(Math.random() * 2)],
        deliveryAddress: `${GOVERNORATES[Math.floor(Math.random() * GOVERNORATES.length)]}, District ${i + 1}`,
        deliveryDate: new Date(Date.now() + Math.random() * 7 * 24 * 60 * 60 * 1000),
        items: {
          create: items,
        },
      },
    });

    orders.push(order);
  }

  return orders;
}

/**
 * Create sample loans
 * إنشاء قروض عينة
 */
async function createLoans(wallets: { id: string }[]) {
  const purposes = [LoanPurpose.SEEDS, LoanPurpose.FERTILIZER, LoanPurpose.EQUIPMENT, LoanPurpose.IRRIGATION];
  const statuses = [LoanStatus.ACTIVE, LoanStatus.PAID, LoanStatus.PENDING];

  for (let i = 0; i < 10; i++) {
    const wallet = wallets[Math.floor(Math.random() * wallets.length)];
    const amount = Math.floor(Math.random() * 2000000) + 500000;
    const termMonths = [3, 6, 12, 18][Math.floor(Math.random() * 4)];

    await prisma.loan.create({
      data: {
        walletId: wallet.id,
        amount,
        interestRate: 0, // Islamic financing - no interest
        totalDue: amount,
        paidAmount: Math.random() > 0.5 ? Math.floor(amount * Math.random()) : 0,
        termMonths,
        startDate: new Date(Date.now() - Math.random() * 90 * 24 * 60 * 60 * 1000),
        dueDate: new Date(Date.now() + termMonths * 30 * 24 * 60 * 60 * 1000),
        purpose: purposes[Math.floor(Math.random() * purposes.length)],
        purposeDetails: 'Agricultural financing for farm improvement',
        collateralType: ['crop', 'equipment', 'land'][Math.floor(Math.random() * 3)],
        collateralValue: amount * 1.2,
        status: statuses[Math.floor(Math.random() * statuses.length)],
      },
    });
  }
}

/**
 * Main seeding function
 * دالة البذر الرئيسية
 */
async function main() {
  console.log('🌱 Starting marketplace database seeding...');
  console.log('🌱 بدء بذر قاعدة بيانات السوق...');

  // Clear existing data
  console.log('🗑️ Clearing existing data...');
  await prisma.reviewResponse.deleteMany();
  await prisma.productReview.deleteMany();
  await prisma.walletAuditLog.deleteMany();
  await prisma.scheduledPayment.deleteMany();
  await prisma.escrow.deleteMany();
  await prisma.creditEvent.deleteMany();
  await prisma.loan.deleteMany();
  await prisma.transaction.deleteMany();
  await prisma.orderItem.deleteMany();
  await prisma.order.deleteMany();
  await prisma.product.deleteMany();
  await prisma.wallet.deleteMany();
  await prisma.buyerProfile.deleteMany();
  await prisma.sellerProfile.deleteMany();

  // Create sellers
  console.log('👨‍🌾 Creating seller profiles...');
  const sellers = await createSellers(10);
  console.log(`   Created ${sellers.length} sellers`);

  // Create buyers
  console.log('🛒 Creating buyer profiles...');
  const buyers = await createBuyers(15);
  console.log(`   Created ${buyers.length} buyers`);

  // Create wallets
  console.log('💰 Creating wallets...');
  const wallets = await createWallets(
    sellers.map(s => s.userId),
    buyers.map(b => b.userId)
  );
  console.log(`   Created ${wallets.length} wallets`);

  // Create products
  console.log('📦 Creating products...');
  const products = await createProducts(sellers);
  console.log(`   Created ${products.length} products`);

  // Create orders
  console.log('📝 Creating orders...');
  const orders = await createOrders(products, buyers);
  console.log(`   Created ${orders.length} orders`);

  // Create loans
  console.log('🏦 Creating loans...');
  await createLoans(wallets);
  console.log('   Created sample loans');

  // Summary
  const productCount = await prisma.product.count();
  const orderCount = await prisma.order.count();
  const walletCount = await prisma.wallet.count();
  const loanCount = await prisma.loan.count();

  console.log('\n✅ Marketplace seeding completed successfully!');
  console.log('✅ اكتمل بذر السوق بنجاح!');
  console.log('─────────────────────────────────────');
  console.log(`📊 Summary / الملخص:`);
  console.log(`   - Sellers / البائعون: ${sellers.length}`);
  console.log(`   - Buyers / المشترون: ${buyers.length}`);
  console.log(`   - Products / المنتجات: ${productCount}`);
  console.log(`   - Orders / الطلبات: ${orderCount}`);
  console.log(`   - Wallets / المحافظ: ${walletCount}`);
  console.log(`   - Loans / القروض: ${loanCount}`);
  console.log('─────────────────────────────────────');
}

main()
  .catch((e) => {
    console.error('❌ Seeding failed:', e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
