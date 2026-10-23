"""Small, clearly labelled demo dataset. Replace with API-backed services for production."""

def build_demo_results(trip: dict, nights: int) -> dict:
    destination = trip["destination"]
    people = int(trip["adults"] + trip["children"])
    # All prices below are illustrative COP values, not live quotes.
    flights = [
        {"airline":"Aerolínea demo A","stops":"Directo","depart":"08:15","arrive":"12:05","duration":"3 h 50 min","baggage":"Equipaje de mano","price":920000},
        {"airline":"Aerolínea demo B","stops":"1 escala","depart":"06:40","arrive":"13:20","duration":"6 h 40 min","baggage":"Equipaje de mano + artículo personal","price":690000},
        {"airline":"Aerolínea demo C","stops":"2+ escalas","depart":"14:10","arrive":"23:35","duration":"9 h 25 min","baggage":"Artículo personal","price":540000},
    ]
    hotels = [
        {"name":"Nómada Urban Stay","kind":"Boutique","rating":"4.7","area":"Zona céntrica","amenities":["Wi-Fi","Desayuno","Recepción 24 h"],"nightly":310000},
        {"name":"Casa Bruma Collection","kind":"Diseño & confort","rating":"4.8","area":"Distrito cultural","amenities":["Piscina","Restaurante","Gimnasio"],"nightly":485000},
        {"name":"Luna Verde Guesthouse","kind":"Económico","rating":"4.5","area":"Barrio local","amenities":["Wi-Fi","Cocina compartida","Terraza"],"nightly":175000},
    ]
    restaurants = [
        {"name":"Mesa de Barrio","cuisine":"Local","price_level":"Económico","rating":"4.6","description":f"Sabores tradicionales y ambiente relajado en {destination}.","avg_cost":55000},
        {"name":"Azul y Maíz","cuisine":"Mexicana","price_level":"Moderado","rating":"4.7","description":"Cocina regional, ingredientes de temporada y platos para compartir.","avg_cost":95000},
        {"name":"Oriente Moderno","cuisine":"Internacional","price_level":"Premium","rating":"4.8","description":"Una propuesta contemporánea ideal para una cena especial.","avg_cost":185000},
        {"name":"Verde Vivo","cuisine":"Vegetariana","price_level":"Moderado","rating":"4.5","description":"Opciones vegetales creativas, frescas y llenas de color.","avg_cost":72000},
    ]
    base = [
        ("09:00","Paseo de orientación","Recorre el centro y descubre sus principales plazas.",0),
        ("12:30","Almuerzo local","Prueba sabores regionales en un restaurante recomendado.",65000),
        ("15:00","Museo o visita cultural","Dedica la tarde a una experiencia cultural de la ciudad.",45000),
        ("18:30","Atardecer panorámico","Termina el día con una vista memorable y tiempo libre.",25000),
    ]
    itinerary=[]
    for day in range(1, min(nights+1, 8)):
        if day == 1: title = "Primer encuentro con la ciudad"
        elif day == 2: title = "Cultura, sabores y rincones locales"
        elif day == 3: title = "Una experiencia fuera de lo común"
        else: title = "Exploración a tu propio ritmo"
        items=[]
        for idx,(time,name,desc,cost) in enumerate(base):
            if day > 1 and idx == 0: name,desc,cost = "Ruta de barrio", "Explora calles, mercados y espacios locales.", 30000
            if day > 2 and idx == 2: name,desc,cost = "Experiencia elegida", "Reserva una actividad según tus intereses.", 95000
            items.append({"time":time,"name":name,"description":desc,"cost":cost})
        itinerary.append({"day":day,"title":title,"items":items})
    flight_cost = 920000 * people
    hotel_cost = 310000 * nights
    food_cost = 150000 * people * nights
    activity_cost = 135000 * people * nights
    local_transport = 65000 * people * nights
    contingency = round((flight_cost+hotel_cost+food_cost+activity_cost+local_transport)*0.1)
    budget_breakdown={"Vuelos":flight_cost,"Hospedaje":hotel_cost,"Gastronomía":food_cost,"Actividades":activity_cost,"Transporte local":local_transport,"Imprevistos (10%)":contingency}
    return {"flights":flights,"hotels":hotels,"restaurants":restaurants,"itinerary":itinerary,"budget_breakdown":budget_breakdown}
