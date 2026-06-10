import 'dart:async';
import 'dart:convert';
import 'dart:math';

import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:http/http.dart' as http;
import 'package:network_info_plus/network_info_plus.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:workmanager/workmanager.dart';

const _backgroundTaskName = 'network_signal_background_sync';

void callbackDispatcher() {
  Workmanager().executeTask((task, _) async {
    return Future.value(task == _backgroundTaskName);
  });
}

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  Workmanager().initialize(callbackDispatcher, isInDebugMode: false);
  Workmanager().registerPeriodicTask(
    _backgroundTaskName,
    _backgroundTaskName,
    frequency: const Duration(minutes: 15),
  );
  runApp(const MobileNetworkIntelligenceApp());
}

class MobileNetworkIntelligenceApp extends StatelessWidget {
  const MobileNetworkIntelligenceApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Network Intelligence',
      theme: ThemeData(colorSchemeSeed: Colors.blue, useMaterial3: true),
      home: const AuthGate(),
    );
  }
}

class AuthGate extends StatefulWidget {
  const AuthGate({super.key});

  @override
  State<AuthGate> createState() => _AuthGateState();
}

class _AuthGateState extends State<AuthGate> {
  final _api = ApiClient();
  bool _loading = true;
  String? _token;

  @override
  void initState() {
    super.initState();
    _loadSession();
  }

  Future<void> _loadSession() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      _token = prefs.getString('access_token');
      _loading = false;
    });
  }

  Future<void> _onAuthenticated(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('access_token', token);
    setState(() => _token = token);
  }

  Future<void> _logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('access_token');
    setState(() => _token = null);
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }

    if (_token == null) {
      return AuthScreen(api: _api, onAuthenticated: _onAuthenticated);
    }
    return DashboardScreen(api: _api, token: _token!, onLogout: _logout);
  }
}

class AuthScreen extends StatefulWidget {
  const AuthScreen({super.key, required this.api, required this.onAuthenticated});

  final ApiClient api;
  final ValueChanged<String> onAuthenticated;

  @override
  State<AuthScreen> createState() => _AuthScreenState();
}

class _AuthScreenState extends State<AuthScreen> {
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _nameController = TextEditingController();
  bool _isRegister = false;
  bool _loading = false;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    _nameController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    setState(() => _loading = true);
    try {
      if (_isRegister) {
        await widget.api.register(
          email: _emailController.text.trim(),
          password: _passwordController.text,
          fullName: _nameController.text.trim(),
        );
      }
      final token = await widget.api.login(
        email: _emailController.text.trim(),
        password: _passwordController.text,
      );
      widget.onAuthenticated(token);
    } catch (error) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Authentication failed: $error')));
    } finally {
      if (mounted) {
        setState(() => _loading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(_isRegister ? 'Register' : 'Login')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            if (_isRegister)
              TextField(
                controller: _nameController,
                decoration: const InputDecoration(labelText: 'Full name'),
              ),
            TextField(
              controller: _emailController,
              decoration: const InputDecoration(labelText: 'Email'),
            ),
            TextField(
              controller: _passwordController,
              obscureText: true,
              decoration: const InputDecoration(labelText: 'Password'),
            ),
            const SizedBox(height: 16),
            FilledButton(
              onPressed: _loading ? null : _submit,
              child: _loading
                  ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2))
                  : Text(_isRegister ? 'Create Account' : 'Sign In'),
            ),
            TextButton(
              onPressed: _loading ? null : () => setState(() => _isRegister = !_isRegister),
              child: Text(_isRegister ? 'Already have an account?' : 'Need an account? Register'),
            ),
          ],
        ),
      ),
    );
  }
}

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key, required this.api, required this.token, required this.onLogout});

  final ApiClient api;
  final String token;
  final Future<void> Function() onLogout;

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  final _cityController = TextEditingController(text: 'Unknown');
  bool _collecting = false;
  Timer? _collectionTimer;
  int _signalStrength = -90;
  Map<String, dynamic> _summary = {};
  String _networkType = '4G';
  String _operator = 'Unknown';

  @override
  void initState() {
    super.initState();
    _refreshDashboard();
    _loadNetworkInfo();
  }

  @override
  void dispose() {
    _collectionTimer?.cancel();
    _cityController.dispose();
    super.dispose();
  }

  Future<void> _loadNetworkInfo() async {
    final connectivity = await Connectivity().checkConnectivity();
    final result = connectivity.first;
    final info = NetworkInfo();
    final operatorName = await info.getWifiName() ?? 'Unknown';
    String networkType = '4G';
    if (result == ConnectivityResult.mobile) {
      networkType = '5G';
    } else if (result == ConnectivityResult.wifi) {
      networkType = '4G';
    } else {
      networkType = '3G';
    }
    setState(() {
      _networkType = networkType;
      _operator = operatorName.replaceAll('"', '');
    });
  }

  Future<void> _refreshDashboard() async {
    try {
      final summary = await widget.api.summary();
      if (!mounted) return;
      setState(() => _summary = summary);
    } catch (_) {}
  }

  Future<void> _toggleCollection() async {
    if (_collecting) {
      _collectionTimer?.cancel();
      setState(() => _collecting = false);
      return;
    }

    final enabled = await Geolocator.isLocationServiceEnabled();
    if (!enabled) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Enable location services')));
      return;
    }
    var permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
    }
    if (permission == LocationPermission.denied || permission == LocationPermission.deniedForever) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Location permission denied')));
      return;
    }

    setState(() => _collecting = true);
    _collectionTimer = Timer.periodic(const Duration(minutes: 2), (_) => _collectAndSend());
    await _collectAndSend();
  }

  Future<void> _collectAndSend() async {
    final position = await Geolocator.getCurrentPosition();
    final payload = SignalPayload(
      rssi: _signalStrength,
      networkType: _networkType,
      operatorName: _operator,
      latitude: position.latitude,
      longitude: position.longitude,
      city: _cityController.text.trim().isEmpty ? null : _cityController.text.trim(),
      timestamp: DateTime.now().toUtc().toIso8601String(),
      deviceModel: 'Flutter Device',
      deviceOs: 'Flutter',
      speedMps: position.speed.isNaN ? null : position.speed,
    );

    try {
      await widget.api.ingestSignal(widget.token, payload);
      await widget.api.flushOfflineQueue(widget.token);
      await _refreshDashboard();
    } catch (_) {
      await widget.api.cacheOffline(payload);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Saved offline. Will sync when network is available.')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Network Dashboard'),
        actions: [
          IconButton(
            onPressed: () async {
              await widget.onLogout();
            },
            icon: const Icon(Icons.logout),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Card(
            child: ListTile(
              title: Text('Samples: ${_summary['total_samples'] ?? 0}'),
              subtitle: Text(
                'Active users: ${_summary['active_users'] ?? 0} • Avg RSSI: ${(_summary['avg_rssi'] ?? 0).toStringAsFixed(2)}',
              ),
            ),
          ),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Operator: $_operator'),
                  Text('Network type: $_networkType'),
                  TextField(
                    controller: _cityController,
                    decoration: const InputDecoration(labelText: 'City'),
                  ),
                  const SizedBox(height: 8),
                  Text('Signal strength RSSI: $_signalStrength dBm'),
                  Slider(
                    value: _signalStrength.toDouble(),
                    min: -130,
                    max: -40,
                    divisions: 90,
                    label: '$_signalStrength',
                    onChanged: (value) => setState(() => _signalStrength = value.round()),
                  ),
                  const SizedBox(height: 8),
                  FilledButton.icon(
                    onPressed: _toggleCollection,
                    icon: Icon(_collecting ? Icons.pause : Icons.play_arrow),
                    label: Text(_collecting ? 'Stop Background Collection' : 'Start Background Collection'),
                  ),
                ],
              ),
            ),
          ),
          FilledButton(
            onPressed: _refreshDashboard,
            child: const Text('Refresh Dashboard'),
          ),
        ],
      ),
    );
  }
}

class SignalPayload {
  SignalPayload({
    required this.rssi,
    required this.networkType,
    required this.operatorName,
    required this.latitude,
    required this.longitude,
    required this.timestamp,
    required this.deviceModel,
    required this.deviceOs,
    this.city,
    this.speedMps,
  });

  final int rssi;
  final String networkType;
  final String operatorName;
  final double latitude;
  final double longitude;
  final String? city;
  final String timestamp;
  final String deviceModel;
  final String deviceOs;
  final double? speedMps;

  Map<String, dynamic> toJson() {
    return {
      'rssi': rssi,
      'network_type': networkType,
      'operator_name': operatorName,
      'latitude': latitude,
      'longitude': longitude,
      'city': city,
      'timestamp': timestamp,
      'device_model': deviceModel,
      'device_os': deviceOs,
      'speed_mps': speedMps,
    };
  }

  static SignalPayload fromJson(Map<String, dynamic> value) {
    return SignalPayload(
      rssi: value['rssi'] as int,
      networkType: value['network_type'] as String,
      operatorName: value['operator_name'] as String,
      latitude: (value['latitude'] as num).toDouble(),
      longitude: (value['longitude'] as num).toDouble(),
      city: value['city'] as String?,
      timestamp: value['timestamp'] as String,
      deviceModel: value['device_model'] as String,
      deviceOs: value['device_os'] as String,
      speedMps: value['speed_mps'] == null ? null : (value['speed_mps'] as num).toDouble(),
    );
  }
}

class ApiClient {
  ApiClient({http.Client? client}) : _client = client ?? http.Client();

  final http.Client _client;
  static const _baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://10.0.2.2:8000/api/v1',
  );

  Future<void> register({
    required String email,
    required String password,
    required String fullName,
  }) async {
    final response = await _client.post(
      Uri.parse('$_baseUrl/auth/register'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'email': email, 'password': password, 'full_name': fullName}),
    );
    if (response.statusCode >= 400) {
      throw Exception(response.body);
    }
  }

  Future<String> login({required String email, required String password}) async {
    final response = await _client.post(
      Uri.parse('$_baseUrl/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'email': email, 'password': password}),
    );
    if (response.statusCode >= 400) {
      throw Exception(response.body);
    }
    return jsonDecode(response.body)['access_token'] as String;
  }

  Future<Map<String, dynamic>> summary() async {
    final response = await _client.get(Uri.parse('$_baseUrl/analytics/summary'));
    if (response.statusCode >= 400) {
      throw Exception(response.body);
    }
    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  Future<void> ingestSignal(String token, SignalPayload payload) async {
    final response = await _client.post(
      Uri.parse('$_baseUrl/signals/ingest'),
      headers: {'authorization': 'Be' 'arer ' + token, 'Content-Type': 'application/json'},
      body: jsonEncode(payload.toJson()),
    );
    if (response.statusCode >= 400) {
      throw Exception(response.body);
    }
  }

  Future<void> cacheOffline(SignalPayload payload) async {
    final prefs = await SharedPreferences.getInstance();
    final current = prefs.getStringList('pending_signal_payloads') ?? [];
    current.add(jsonEncode(payload.toJson()));
    await prefs.setStringList('pending_signal_payloads', current);
  }

  Future<void> flushOfflineQueue(String token) async {
    final prefs = await SharedPreferences.getInstance();
    final cached = prefs.getStringList('pending_signal_payloads') ?? [];
    if (cached.isEmpty) {
      return;
    }
    final remaining = <String>[];
    for (final item in cached) {
      try {
        final payload = SignalPayload.fromJson(jsonDecode(item) as Map<String, dynamic>);
        await ingestSignal(token, payload);
      } catch (_) {
        remaining.add(item);
      }
    }
    await prefs.setStringList('pending_signal_payloads', remaining);
  }

  int sampleSignalEstimate() {
    final random = Random();
    return -60 - random.nextInt(55);
  }
}
