from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPBadRequest
from datetime import datetime
from worq.models.models import Requests, Status

@view_config(route_name='submit_request', request_method='POST')
def submit_request(request):
    try:
        # Recolectar datos del formulario
        task_id_str = request.POST.get('task_id')
        status_id_str = request.POST.get('status_id')
        action_type = request.POST.get('action_type')
        reason = request.POST.get('reason')

        # Recolectar datos de sesión
        print(f"User session data: {request.session}")  # Verificar los datos de la sesión
        user_id = request.session.get('user_id')
        project_id = request.session.get('project_id')

        status_id = 1
        missing_fields = []

        # Verificar si faltan campos y agregarlos a la lista
        if not task_id_str:
            missing_fields.append("task_id")
        if not action_type:
            missing_fields.append("action_type")
        if not reason:
            missing_fields.append("reason")
        if not user_id:
            missing_fields.append("user_id")
        if not project_id:
            missing_fields.append("project_id")

        # Si hay campos faltantes, devolver el error especificando qué falta
        if missing_fields:
            raise ValueError(f"Faltan los siguientes datos requeridos: {', '.join(missing_fields)}.")

        # Convertir strings a enteros
        task_id = int(task_id_str)

        # Crear nueva solicitud
        new_request = Requests(
            user_id=user_id,
            project_id=project_id,
            status_id=status_id,
            action_type=action_type,
            reason=reason,
            request_date=datetime.now(),
            task_id=task_id
        )

        # Guardar en base de datos
        request.dbsession.add(new_request)

        # Redirigir a la vista de tareas
        return HTTPFound(location=request.route_url('task_view'))

    except Exception as e:
        print(f"Error en submit_request: {e}")
        raise HTTPBadRequest(f"Error al procesar la solicitud: {str(e)}")
