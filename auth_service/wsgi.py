from auth_service import create_app

app = create_app()

if __name__ == '__main__':
    import pdb; pdb.set_trace()  # Punto de interrupción para debug
    app.run(host='0.0.0.0', port=8000, debug=True) 