/// Movement Tile Widget - عنصر حركة المخزون
library;

import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../data/inventory_models.dart';

/// عنصر عرض حركة مخزون
class MovementTile extends StatelessWidget {
  final StockMovement movement;
  final VoidCallback? onTap;

  const MovementTile({
    super.key,
    required this.movement,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final locale = Localizations.localeOf(context).languageCode;
    final dateFormat = DateFormat('dd/MM/yyyy HH:mm', locale);

    return ListTile(
      onTap: onTap,
      leading: _buildLeadingIcon(context),
      title: Row(
        children: [
          Expanded(
            child: Text(
              movement.movementType.getName(locale),
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
          ),
          Text(
            '${movement.isStockIncrease ? '+' : '-'}${movement.quantity.toStringAsFixed(1)} ${movement.unit.getName(locale)}',
            style: TextStyle(
              fontWeight: FontWeight.bold,
              color: movement.isStockIncrease ? Colors.green.shade700 : Colors.red.shade700,
              fontSize: 16,
            ),
          ),
        ],
      ),
      subtitle: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SizedBox(height: 4),
          // التاريخ والمستخدم
          Row(
            children: [
              Icon(Icons.calendar_today, size: 12, color: Colors.grey.shade600),
              const SizedBox(width: 4),
              Text(
                dateFormat.format(movement.movementDate),
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.grey.shade600,
                ),
              ),
              if (movement.userName != null) ...[
                const SizedBox(width: 8),
                Icon(Icons.person, size: 12, color: Colors.grey.shade600),
                const SizedBox(width: 4),
                Text(
                  movement.userName!,
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey.shade600,
                  ),
                ),
              ],
            ],
          ),
          // الحقل إذا كان تطبيق حقلي
          if (movement.fieldName != null) ...[
            const SizedBox(height: 2),
            Row(
              children: [
                Icon(Icons.landscape, size: 12, color: Colors.green.shade600),
                const SizedBox(width: 4),
                Text(
                  movement.fieldName!,
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.green.shade700,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ],
          // الملاحظات
          if (movement.getNotes(locale) != null) ...[
            const SizedBox(height: 2),
            Text(
              movement.getNotes(locale)!,
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey.shade700,
                fontStyle: FontStyle.italic,
              ),
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
          ],
          // المخزون السابق والجديد
          if (movement.previousStock != null && movement.newStock != null) ...[
            const SizedBox(height: 4),
            Row(
              children: [
                Text(
                  'المخزون: ${movement.previousStock!.toStringAsFixed(1)}',
                  style: TextStyle(
                    fontSize: 11,
                    color: Colors.grey.shade600,
                  ),
                ),
                Icon(
                  Icons.arrow_forward,
                  size: 12,
                  color: Colors.grey.shade600,
                ),
                Text(
                  movement.newStock!.toStringAsFixed(1),
                  style: TextStyle(
                    fontSize: 11,
                    color: Colors.grey.shade800,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ],
        ],
      ),
      trailing: movement.reference != null
          ? Chip(
              label: Text(
                movement.reference!,
                style: const TextStyle(fontSize: 10),
              ),
              visualDensity: VisualDensity.compact,
            )
          : null,
    );
  }

  Widget _buildLeadingIcon(BuildContext context) {
    IconData icon;
    Color color;

    switch (movement.movementType) {
      case MovementType.stockIn:
        icon = Icons.arrow_downward;
        color = Colors.green;
        break;
      case MovementType.stockOut:
        icon = Icons.arrow_upward;
        color = Colors.red;
        break;
      case MovementType.fieldApplication:
        icon = Icons.agriculture;
        color = Colors.blue;
        break;
      case MovementType.adjustment:
        icon = Icons.tune;
        color = Colors.orange;
        break;
      case MovementType.damaged:
        icon = Icons.warning;
        color = Colors.red.shade700;
        break;
      case MovementType.expired:
        icon = Icons.event_busy;
        color = Colors.grey;
        break;
      case MovementType.transfer:
        icon = Icons.swap_horiz;
        color = Colors.purple;
        break;
      case MovementType.returned:
        icon = Icons.keyboard_return;
        color = Colors.teal;
        break;
    }

    return CircleAvatar(
      backgroundColor: color.withOpacity(0.15),
      child: Icon(
        icon,
        color: color.shade700,
        size: 20,
      ),
    );
  }
}
