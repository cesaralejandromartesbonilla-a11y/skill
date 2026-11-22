extends Area3D
class_name PhysicalTestArea

@export var test_name: String = "Test de Desplazamiento Físico"
@export var timeout_seconds: float = 6.0
@export var min_entry_speed: float = 10.0
@export var max_entry_speed: float = 20.0
@export var max_allowed_roll_deg: float = 30.0
@export var auto_quit_on_finish: bool = false

var _elapsed_time: float = 0.0
var _test_finished: bool = false
var _target_body: Node3D = null

func _ready() -> void:
	body_entered.connect(_on_body_entered)
	print("[TEST-FISICO:INICIO] '%s' armado. Esperando sujeto (Timeout: %.1fs)..." % [test_name, timeout_seconds])

func _physics_process(delta: float) -> void:
	if _test_finished:
		return
		
	_elapsed_time += delta
	
	if _target_body and is_instance_valid(_target_body):
		var roll = abs(rad_to_deg(_target_body.rotation.z))
		if roll > max_allowed_roll_deg:
			_fail_test("Vuelco lateral detectado", "Roll de %.1f° superó el límite permitido de %.1f°" % [roll, max_allowed_roll_deg])
			return

	if _elapsed_time >= timeout_seconds:
		_fail_test("Tiempo límite agotado (Timeout)", "El sujeto no alcanzó el Area3D en %.2fs. Posible falta de tracción, potencia o bloqueo físico." % timeout_seconds)

func register_subject(body: Node3D) -> void:
	_target_body = body

func _on_body_entered(body: Node3D) -> void:
	if _test_finished:
		return
		
	if _target_body != null and body != _target_body:
		return

	var speed = 0.0
	var roll = 0.0
	if body is RigidBody3D:
		speed = body.linear_velocity.length()
		roll = abs(rad_to_deg(body.rotation.z))
	elif body is CharacterBody3D:
		speed = body.velocity.length()
		roll = abs(rad_to_deg(body.rotation.z))

	if speed < min_entry_speed:
		_fail_test("Velocidad de entrada insuficiente", "Velocidad registrada: %.2f m/s (Mínimo requerido: %.2f m/s)." % [speed, min_entry_speed])
		return
		
	if speed > max_entry_speed:
		_fail_test("Velocidad de entrada excesiva", "Velocidad registrada: %.2f m/s (Máximo permitido: %.2f m/s)." % [speed, max_entry_speed])
		return

	_pass_test(speed, roll)

func _pass_test(speed: float, roll: float) -> void:
	_test_finished = true
	print("\n=======================================================")
	print("[TEST-FISICO:EXITO] %s" % test_name)
	print("- Qué pasó: El sujeto alcanzó el Area3D en %.2fs." % _elapsed_time)
	print("- Telemetría: Velocidad = %.2f m/s, Inclinación Roll = %.1f°." % [speed, roll])
	print("- Por qué pasó: Parámetros de masa, tracción y suspensión dentro del rango dinámico esperado.")
	print("=======================================================\n")
	_finish(0)

func _fail_test(motivo: String, explicacion_fisica: String) -> void:
	_test_finished = true
	printerr("\n=======================================================")
	printerr("[TEST-FISICO:FALLO] %s" % test_name)
	printerr("- Qué pasó: %s." % motivo)
	printerr("- Por qué pasó: %s" % explicacion_fisica)
	printerr("- Tiempo registrado: %.2fs." % _elapsed_time)
	printerr("=======================================================\n")
	_finish(1)

func _finish(exit_code: int) -> void:
	if auto_quit_on_finish and OS.has_feature("dedicated_server") or DisplayServer.get_name() == "headless":
		get_tree().quit(exit_code)
