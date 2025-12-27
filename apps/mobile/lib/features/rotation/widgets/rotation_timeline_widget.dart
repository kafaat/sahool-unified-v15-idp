import 'package:flutter/material.dart';
import '../models/rotation_models.dart';

class RotationTimelineWidget extends StatelessWidget {
  final List<RotationYear> rotationYears;
  final int selectedIndex;
  final Function(int) onYearSelected;

  const RotationTimelineWidget({
    Key? key,
    required this.rotationYears,
    required this.selectedIndex,
    required this.onYearSelected,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 140,
      decoration: BoxDecoration(
        color: Colors.grey.shade50,
        border: Border(
          top: BorderSide(color: Colors.grey.shade300),
          bottom: BorderSide(color: Colors.grey.shade300),
        ),
      ),
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        itemCount: rotationYears.length,
        itemBuilder: (context, index) {
          final year = rotationYears[index];
          final isSelected = index == selectedIndex;
          final isPast = year.isCompleted;
          final isCurrent = year.isCurrent;
          final isFuture = !isPast && !isCurrent;

          return GestureDetector(
            onTap: () => onYearSelected(index),
            child: Container(
              width: 100,
              margin: const EdgeInsets.only(right: 12),
              child: Column(
                children: [
                  // Year badge
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 12,
                      vertical: 6,
                    ),
                    decoration: BoxDecoration(
                      color: isSelected
                          ? _getYearColor(year)
                          : Colors.grey.shade300,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(
                        color: isSelected
                            ? _getYearColor(year)
                            : Colors.grey.shade400,
                        width: 2,
                      ),
                    ),
                    child: Text(
                      year.year.toString(),
                      style: TextStyle(
                        color: isSelected ? Colors.white : Colors.grey.shade700,
                        fontWeight: FontWeight.bold,
                        fontSize: 14,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ),

                  const SizedBox(height: 8),

                  // Crop icon
                  Container(
                    width: 56,
                    height: 56,
                    decoration: BoxDecoration(
                      color: isSelected
                          ? _getYearColor(year).withOpacity(0.2)
                          : Colors.white,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(
                        color: isSelected
                            ? _getYearColor(year)
                            : Colors.grey.shade300,
                        width: 2,
                      ),
                    ),
                    child: year.crop != null
                        ? _buildCropIcon(year.crop!, isSelected, year)
                        : Icon(
                            Icons.help_outline,
                            color: Colors.grey.shade400,
                            size: 28,
                          ),
                  ),

                  const SizedBox(height: 6),

                  // Crop name
                  if (year.crop != null)
                    Text(
                      year.crop!.nameEn,
                      style: TextStyle(
                        fontSize: 11,
                        fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                        color: isSelected
                            ? _getYearColor(year)
                            : Colors.grey.shade700,
                      ),
                      textAlign: TextAlign.center,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    )
                  else
                    Text(
                      'Unplanned',
                      style: TextStyle(
                        fontSize: 11,
                        fontStyle: FontStyle.italic,
                        color: Colors.grey.shade500,
                      ),
                    ),

                  // Season indicator
                  if (year.season.isNotEmpty)
                    Container(
                      margin: const EdgeInsets.only(top: 2),
                      padding: const EdgeInsets.symmetric(
                        horizontal: 6,
                        vertical: 2,
                      ),
                      decoration: BoxDecoration(
                        color: _getSeasonColor(year.season).withOpacity(0.2),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        _getSeasonIcon(year.season),
                        style: TextStyle(
                          fontSize: 10,
                          color: _getSeasonColor(year.season),
                        ),
                      ),
                    ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildCropIcon(Crop crop, bool isSelected, RotationYear year) {
    // Different icons for different crop families
    IconData icon;
    Color iconColor;

    switch (crop.family) {
      case CropFamily.poaceae:
        icon = Icons.grass;
        iconColor = Colors.amber;
        break;
      case CropFamily.fabaceae:
        icon = Icons.eco;
        iconColor = Colors.green;
        break;
      case CropFamily.solanaceae:
        icon = Icons.local_florist;
        iconColor = Colors.red;
        break;
      case CropFamily.alliaceae:
        icon = Icons.dining;
        iconColor = Colors.purple;
        break;
      case CropFamily.rubiaceae:
      case CropFamily.celastraceae:
        icon = Icons.coffee;
        iconColor = Colors.brown;
        break;
      case CropFamily.brassicaceae:
        icon = Icons.park;
        iconColor = Colors.lightGreen;
        break;
      case CropFamily.cucurbitaceae:
        icon = Icons.nature;
        iconColor = Colors.orange;
        break;
      default:
        icon = Icons.agriculture;
        iconColor = Colors.green;
    }

    return Stack(
      children: [
        Center(
          child: Icon(
            icon,
            color: isSelected ? _getYearColor(year) : iconColor,
            size: 32,
          ),
        ),
        if (year.isCurrent)
          Positioned(
            right: 2,
            top: 2,
            child: Container(
              width: 12,
              height: 12,
              decoration: BoxDecoration(
                color: Colors.orange,
                shape: BoxShape.circle,
                border: Border.all(color: Colors.white, width: 1.5),
              ),
            ),
          ),
        if (year.isCompleted)
          Positioned(
            right: 2,
            bottom: 2,
            child: Container(
              padding: const EdgeInsets.all(2),
              decoration: BoxDecoration(
                color: Colors.green,
                shape: BoxShape.circle,
                border: Border.all(color: Colors.white, width: 1.5),
              ),
              child: const Icon(
                Icons.check,
                color: Colors.white,
                size: 8,
              ),
            ),
          ),
      ],
    );
  }

  Color _getYearColor(RotationYear year) {
    if (year.isCurrent) return Colors.green;
    if (year.isCompleted) return Colors.grey;
    return Colors.blue;
  }

  Color _getSeasonColor(String season) {
    switch (season.toLowerCase()) {
      case 'spring':
        return Colors.lightGreen;
      case 'summer':
        return Colors.orange;
      case 'fall':
      case 'autumn':
        return Colors.brown;
      case 'winter':
        return Colors.blue;
      default:
        return Colors.grey;
    }
  }

  String _getSeasonIcon(String season) {
    switch (season.toLowerCase()) {
      case 'spring':
        return '🌸';
      case 'summer':
        return '☀️';
      case 'fall':
      case 'autumn':
        return '🍂';
      case 'winter':
        return '❄️';
      default:
        return '📅';
    }
  }
}
