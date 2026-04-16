// ═══════════════════════════════════════════════════════════════════════════════
// SAHOOL EventCatalog Configuration
// تكوين كتالوج الأحداث – سهول
//
// Synced from governance/events/catalog.yaml
// via scripts/sync-eventcatalog-from-governance.py
// ═══════════════════════════════════════════════════════════════════════════════

/** @type {import('@eventcatalog/core/bin/eventcatalog.config').Config} */
module.exports = {
  title: 'SAHOOL Event Catalog',
  tagline:
    'Event-driven architecture catalog for the National Agricultural Intelligence Platform',
  organizationName: 'KAFAAT / SAHOOL',
  homepageLink: 'https://app.sahool.io',
  editUrl: 'https://github.com/kafaat/sahool-unified-v15-idp/edit/main/idp/eventcatalog',
  logo: {
    alt: 'SAHOOL Logo',
    src: '/logo.png',
  },
  primaryCTA: {
    label: 'Explore Events',
    href: '/events',
  },
  secondaryCTA: {
    label: 'Explore Services',
    href: '/services',
  },
  generators: [
    // Governance sync is handled by scripts/sync-eventcatalog-from-governance.py
  ],
  users: [
    {
      id: 'platform-team',
      name: 'Platform Team',
      role: 'Platform Engineering',
    },
    {
      id: 'agro-team',
      name: 'Agro Team',
      role: 'Agricultural Intelligence',
    },
    {
      id: 'iot-team',
      name: 'IoT Team',
      role: 'IoT & Edge Computing',
    },
    {
      id: 'frontend-team',
      name: 'Frontend Team',
      role: 'Web & Mobile',
    },
  ],
};
