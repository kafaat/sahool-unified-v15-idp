// AUTO-GENERATED - DO NOT EDIT MANUALLY
// Generated from one approved OpenAPI GET operation for the SAHOOL Low-Code Builder PoC.
// This widget renders caller-provided rows only; it does not perform API calls.
// TENANT_ID_REQUIRED
// PERMISSION_CHECK_REQUIRED

import 'package:flutter/material.dart';

class ListFieldsLowCodeCardList extends StatelessWidget {
  const ListFieldsLowCodeCardList({
    super.key,
    required this.tenantId,
    required this.permissions,
    required this.rows,
    this.onRefresh,
  });

  static const requiredPermission = "listFields:read";
  final String tenantId;
  final Set<String> permissions;
  final List<Map<String, Object?>> rows;
  final VoidCallback? onRefresh;

  @override
  Widget build(BuildContext context) {
    if (tenantId.trim().isEmpty) {
      return const _LowCodeGuardMessage(message: 'Tenant context is required before UI generation.');
    }
    if (!permissions.contains(requiredPermission)) {
      return const _LowCodeGuardMessage(message: 'Missing permission for generated view.');
    }

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Row(
          children: [
            Expanded(child: Text("List fields", style: Theme.of(context).textTheme.titleLarge)),
            IconButton(
              // PERMISSION_CHECK_REQUIRED
              onPressed: onRefresh,
              icon: const Icon(Icons.refresh),
              tooltip: 'Refresh / تحديث',
            ),
          ],
        ),
        const SizedBox(height: 16),
        if (rows.isEmpty)
          const Card(
            child: Padding(
              padding: EdgeInsets.all(16),
              child: Text('No records / لا توجد سجلات'),
            ),
          )
        else
          for (final row in rows)
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Id: ${row["id"] ?? ''}',
                    ),
                    Text(
                      'Name: ${row["name"] ?? ''}',
                    ),
                    Text(
                      'Name Ar: ${row["nameAr"] ?? ''}',
                    ),
                    Text(
                      'Tenant Id: ${row["tenantId"] ?? ''}',
                    ),
                    Text(
                      'Farm Id: ${row["farmId"] ?? ''}',
                    ),
                    Text(
                      'Owner Id: ${row["ownerId"] ?? ''}',
                    ),
                  ],
                ),
              ),
            ),
      ],
    );
  }
}

class _LowCodeGuardMessage extends StatelessWidget {
  const _LowCodeGuardMessage({required this.message});

  final String message;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Text(message),
      ),
    );
  }
}
