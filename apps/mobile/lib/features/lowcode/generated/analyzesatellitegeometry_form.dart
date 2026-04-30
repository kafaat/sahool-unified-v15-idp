// AUTO-GENERATED - DO NOT EDIT MANUALLY
// Generated from one OpenAPI operation for the SAHOOL Low-Code PoC.
// This widget intentionally emits form data via onSubmit; it does not perform API calls.

import 'package:flutter/material.dart';

class AnalyzeSatelliteGeometryLowCodeForm extends StatefulWidget {
  const AnalyzeSatelliteGeometryLowCodeForm({
    super.key,
    required this.tenantId,
    required this.permissions,
    required this.onSubmit,
  });

  final String tenantId;
  final Set<String> permissions;
  final ValueChanged<Map<String, Object?>> onSubmit;

  @override
  State<AnalyzeSatelliteGeometryLowCodeForm> createState() => _AnalyzeSatelliteGeometryLowCodeFormState();
}

class _AnalyzeSatelliteGeometryLowCodeFormState extends State<AnalyzeSatelliteGeometryLowCodeForm> {
  static const requiredPermission = "analyzeSatelliteGeometry:write";
  final _formKey = GlobalKey<FormState>();
  final _geometryController = TextEditingController();
  final _dateController = TextEditingController();
  final _indicesController = TextEditingController();
  String? _satellite = "sentinel2";
  final _cloudCoverMaxController = TextEditingController();

  @override
  void dispose() {
    _geometryController.dispose();
    _dateController.dispose();
    _indicesController.dispose();
    _cloudCoverMaxController.dispose();
    super.dispose();
  }

  void _submit() {
    if (!_formKey.currentState!.validate()) {
      return;
    }
    widget.onSubmit(<String, Object?>{
      'tenantId': widget.tenantId,
      'operationId': "analyzeSatelliteGeometry",
      'method': "POST",
      'path': "/api/v1/satellite/v1/analyze",
      "geometry": _geometryController.text.trim(),
      "date": _dateController.text.trim(),
      "indices": _indicesController.text.trim(),
      "satellite": _satellite,
      "cloudCoverMax": double.tryParse(_cloudCoverMaxController.text),
    });
  }

  @override
  Widget build(BuildContext context) {
    if (widget.tenantId.trim().isEmpty) {
      return const _LowCodeGuardMessage(message: 'Tenant context is required before UI generation.');
    }
    if (!widget.permissions.contains(requiredPermission)) {
      return const _LowCodeGuardMessage(message: 'Missing permission for generated form.');
    }

    return Form(
      key: _formKey,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Text("Analyze an arbitrary polygon", style: Theme.of(context).textTheme.titleLarge),
          const SizedBox(height: 16),
          TextFormField(
            controller: _geometryController,
            decoration: const InputDecoration(labelText: "Geometry"),
            keyboardType: TextInputType.text,
            maxLines: 3,
            validator: (value) => value == null || value.trim().isEmpty ? 'Required' : null,
          ),
          TextFormField(
            controller: _dateController,
            decoration: const InputDecoration(labelText: "Date"),
            keyboardType: TextInputType.text,
            maxLines: 1,
            validator: null,
          ),
          TextFormField(
            controller: _indicesController,
            decoration: const InputDecoration(labelText: "Indices"),
            keyboardType: TextInputType.text,
            maxLines: 3,
            validator: null,
          ),
          DropdownButtonFormField<String>(
            value: _satellite,
            decoration: const InputDecoration(labelText: "Satellite"),
            items: [DropdownMenuItem(value: "sentinel2", child: Text("sentinel2")), DropdownMenuItem(value: "landsat8", child: Text("landsat8")), DropdownMenuItem(value: "landsat9", child: Text("landsat9")), DropdownMenuItem(value: "auto", child: Text("auto"))],
            validator: null,
            onChanged: (value) => setState(() => _satellite = value),
          ),
          TextFormField(
            controller: _cloudCoverMaxController,
            decoration: const InputDecoration(labelText: "Cloudcovermax"),
            keyboardType: TextInputType.number,
            maxLines: 1,
            validator: null,
          ),
          const SizedBox(height: 24),
          FilledButton.icon(
            onPressed: _submit,
            icon: const Icon(Icons.check),
            label: const Text('Submit'),
          ),
        ],
      ),
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
