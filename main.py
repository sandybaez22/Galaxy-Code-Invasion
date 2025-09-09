import pygame
import random
import math
import sys
import os
import json
from pygame import gfxdraw

# Inicialización
pygame.init()
pygame.mixer.init()

# Configuración de la ventana
ANCHO, ALTO = 800, 600
pantalla_completa = False
PANTALLA = pygame.display.set_mode((ANCHO, ALTO), pygame.RESIZABLE)
pygame.display.set_caption("GALAXY CODE: INVASION")

# Configuración del icono de la ventana
try:
    icon_path = os.path.join("assets", "images", "icono.png")
    if os.path.exists(icon_path):
        icono = pygame.image.load(icon_path).convert_alpha()
        pygame.display.set_icon(icono)
    else:
        print(f"Archivo de icono no encontrado en: {icon_path}")
except Exception as e:
    print(f"Error al cargar el icono: {e}")

RELOJ = pygame.time.Clock()

# Directorios de recursos
IMG_DIR = os.path.join("assets", "images")
SND_DIR = os.path.join("assets", "sounds")

# Cargar imágenes
def cargar_imagen(nombre):
    try:
        return pygame.image.load(os.path.join(IMG_DIR, nombre)).convert_alpha()
    except Exception as e:
        print(f"Error al cargar imagen {nombre}: {e}")
        # Crear una imagen de reemplazo
        surf = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.rect(surf, (255, 0, 0), (0, 0, 50, 50), 2)
        return surf

# Cargar sonidos
def cargar_sonido(nombre):
    try:
        return pygame.mixer.Sound(os.path.join(SND_DIR, nombre))
    except Exception as e:
        print(f"Error al cargar sonido {nombre}: {e}")
        return None

# Cargar todos los recursos
nave_img = cargar_imagen("nave.png")
nave_img2 = cargar_imagen("nave2.png")
nave_img3 = cargar_imagen("nave3.png")
nave_img4 = cargar_imagen("nave4.png")  # Nueva skin 1
nave_img5 = cargar_imagen("nave5.png")  # Nueva skin 2
roca_img = cargar_imagen("roca.png")
fondo_img = pygame.image.load(os.path.join(IMG_DIR, "fondo.png")).convert()
fondo_lejano_img = pygame.image.load(os.path.join(IMG_DIR, "fondo_lejano.png")).convert() if os.path.exists(os.path.join(IMG_DIR, "fondo_lejano.png")) else None
game_over_img = cargar_imagen("game_over.png")
explosion_img = cargar_imagen("explosion.png")

# Imágenes para mejoras
velocidad_icon_img = cargar_imagen("velocidad_icon.png")
disparo_icon_img = cargar_imagen("disparo_icon.png")
vida_icon_img = cargar_imagen("vida_icon.png")

# Imágenes opcionales para powerups (si no existen, se dibuja placeholder)
power_doble_img = cargar_imagen("power_doble.png")
power_escudo_img = cargar_imagen("power_escudo.png")
power_vida_img = cargar_imagen("power_vida.png")

sonido_disparo = cargar_sonido("disparo.wav")
sonido_explosion = cargar_sonido("explosion.wav")
sonido_menu = cargar_sonido("musica_menu.wav")
sonido_game_over = cargar_sonido("game_over.wav")
sonido_powerup = cargar_sonido("powerup.wav")
sonido_enemigo_especial = cargar_sonido("enemigo_especial.wav") or sonido_explosion
sonido_disparo_enemigo = cargar_sonido("disparo_enemigo.wav") or sonido_disparo

# Fuentes
try:
    fuente = pygame.font.SysFont("consolas", 28)
    fuente_titulo = pygame.font.SysFont("consolas", 50, bold=True)
    fuente_game_over = pygame.font.SysFont("arial", 36, bold=True)
    fuente_carga = pygame.font.SysFont("consolas", 24)
    fuente_pequena = pygame.font.SysFont("consolas", 18)
except Exception as e:
    print(f"Error al cargar fuentes: {e}")
    fuente = pygame.font.Font(None, 28)
    fuente_titulo = pygame.font.Font(None, 50)
    fuente_game_over = pygame.font.Font(None, 36)
    fuente_carga = pygame.font.Font(None, 24)
    fuente_pequena = pygame.font.Font(None, 18)
    

# Efectos de partículas mejorados
class Particula:
    def __init__(self, x, y, color, size=None, speed=None, angle=None, life=None):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 5) if size is None else size
        self.speed = random.uniform(1, 3) if speed is None else speed
        self.angle = random.uniform(0, math.pi * 2) if angle is None else angle
        self.life = random.randint(20, 40) if life is None else life
        self.max_life = self.life
        self.gravity = random.uniform(-0.05, 0.1)
        self.fade_out = random.choice([True, False])
    
    def update(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed + self.gravity
        self.life -= 1
        return self.life > 0
    
    def draw(self, surface):
        if self.fade_out:
            alpha = min(255, self.life * 6)
            color = (*self.color[:3], alpha)
        else:
            progress = 1 - (self.life / self.max_life)
            if len(self.color) == 4:
                base_color = self.color[:3]
            else:
                base_color = self.color
            end_color = (255, 50, 0) if base_color[0] > 200 else (base_color[0]//2, base_color[1]//3, base_color[2]//2)
            color = (
                int(base_color[0] + (end_color[0] - base_color[0]) * progress),
                int(base_color[1] + (end_color[1] - base_color[1]) * progress),
                int(base_color[2] + (end_color[2] - base_color[2]) * progress)
            )
        
        pygame.gfxdraw.filled_circle(surface, int(self.x), int(self.y), self.size, color)
        if random.random() < 0.3:
            pygame.gfxdraw.circle(surface, int(self.x), int(self.y), self.size + 1, 
                                (min(255, color[0] + 50), min(255, color[1] + 50), min(255, color[2] + 50), 50))

class Explosion:
    def __init__(self, x, y, size_scale=1.0, particle_count=50):
        self.particulas = []
        self.x = x
        self.y = y
        self.frame = 0
        self.max_frames = 15
        colors = [(255, 100, 0), (255, 200, 0), (255, 50, 0), (255, 150, 50)]
        
        for _ in range(particle_count):
            color = random.choice(colors)
            self.particulas.append(Particula(
                x, y, color,
                size=random.randint(1, int(6 * size_scale)),
                speed=random.uniform(0.5, 4 * size_scale),
                angle=random.uniform(0, math.pi * 2),
                life=random.randint(15, int(60 * size_scale))
            ))
    
    def update(self):
        self.frame += 1
        self.particulas = [p for p in self.particulas if p.update()]
        return self.frame < self.max_frames or len(self.particulas) > 0
    
    def draw(self, surface):
        for p in self.particulas:
            p.draw(surface)
        
        if self.frame < self.max_frames:
            size = int(50 * (1 - self.frame / self.max_frames))
            if size > 0:
                img = pygame.transform.scale(explosion_img, (size, size))
                img.set_alpha(200 - (self.frame * 10))
                rect = img.get_rect(center=(self.x, self.y))
                surface.blit(img, rect)

# Sistema de fondo parallax
class FondoParallax:
    def __init__(self):
        self.capas = []
        if fondo_lejano_img:
            self.capas.append({
                'imagen': fondo_lejano_img,
                'velocidad': 0.2,
                'x': 0,
                'y': 0,
                'duplicado_x': fondo_lejano_img.get_width()
            })
        
        self.capas.append({
            'imagen': fondo_img,
            'velocidad': 0.5,
            'x': 0,
            'y': 0,
            'duplicado_x': fondo_img.get_width()
        })
        
        self.estrellas_rapidas = [(random.randint(0, ANCHO), random.randint(0, ALTO), 
                                 random.uniform(1.5, 3.0)) for _ in range(50)]
    
    def actualizar(self):
        for capa in self.capas:
            capa['x'] -= capa['velocidad']
            if capa['x'] <= -capa['imagen'].get_width():
                capa['x'] = 0
        
        for i, (x, y, speed) in enumerate(self.estrellas_rapidas):
            x = (x - speed) % ANCHO
            self.estrellas_rapidas[i] = (x, y, speed)
    
    def dibujar(self, superficie):
        for capa in self.capas:
            superficie.blit(capa['imagen'], (capa['x'], capa['y']))
            superficie.blit(capa['imagen'], (capa['x'] + capa['duplicado_x'], capa['y']))
        
        for x, y, speed in self.estrellas_rapidas:
            alpha = int(100 + 155 * (speed / 3.0))
            size = 1 if speed < 2 else 2
            pygame.draw.circle(superficie, (alpha, alpha, alpha), (x, y), size)

# Clases del juego
class Aspecto:
    def __init__(self, nombre, imagen, precio, desbloqueado=False):
        self.nombre = nombre
        self.imagen = imagen
        self.precio = precio
        self.desbloqueado = desbloqueado

class Mejora:
    def __init__(self, nombre, descripcion, precio_base, nivel_max=5, imagen=None):
        self.nombre = nombre
        self.descripcion = descripcion
        self.precio_base = precio_base
        self.nivel_max = nivel_max
        self.nivel = 0
        self.imagen = imagen
    
    def precio_actual(self):
        return self.precio_base * (self.nivel + 1)
    
    def mejorar(self):
        if self.nivel < self.nivel_max:
            self.nivel += 1
            return True
        return False

class PantallaCarga:
    def __init__(self, mensaje="Cargando recursos..."):
        self.nave_img = pygame.transform.scale(nave_img, (50, 50))
        self.nave_rect = self.nave_img.get_rect(center=(ANCHO//2, ALTO//2))
        self.balas = []
        self.enemigos = []
        self.tiempo_ultimo_disparo = 0
        self.tiempo_ultimo_enemigo = 0
        self.cargando = True
        self.progreso = 0
        self.texto = mensaje
        
        self.mensajes_carga = [
            "Cargando recursos gráficos...",
            "Preparando física del juego...",
            "Inicializando enemigos...",
            "Casi listo...",
            "Preparando la galaxia...",
            "Configurando controles..."
        ]
        
        self.estrellas = [(random.randint(0, ANCHO), random.randint(0, ALTO), random.uniform(0.2, 1)) 
                         for _ in range(100)]
        
        # Movimiento automático
        self.direccion_nave = 1  # 1 para derecha, -1 para izquierda
        self.velocidad_nave = 2
    
    def actualizar(self):
        # Movimiento automático de la nave
        self.nave_rect.x += self.velocidad_nave * self.direccion_nave
        
        # Cambiar dirección si llega a los bordes
        if self.nave_rect.right > ANCHO:
            self.direccion_nave = -1
        elif self.nave_rect.left < 0:
            self.direccion_nave = 1
        
        # Generar enemigos automáticamente
        tiempo_actual = pygame.time.get_ticks()
        if tiempo_actual - self.tiempo_ultimo_enemigo > 1000:
            self.enemigos.append(pygame.Rect(random.randint(0, ANCHO), -40, 40, 40))
            self.tiempo_ultimo_enemigo = tiempo_actual
        
        # Generar disparos automáticamente
        if tiempo_actual - self.tiempo_ultimo_disparo > 500:
            self.balas.append(pygame.Rect(self.nave_rect.centerx - 2, self.nave_rect.top, 4, 10))
            self.tiempo_ultimo_disparo = tiempo_actual
        
        for bala in self.balas[:]:
            bala.y -= 7
            if bala.bottom < 0:
                self.balas.remove(bala)
        
        for enemigo in self.enemigos[:]:
            enemigo.y += 3
            if enemigo.top > ALTO:
                self.enemigos.remove(enemigo)
        
        for bala in self.balas[:]:
            for enemigo in self.enemigos[:]:
                if bala.colliderect(enemigo):
                    if bala in self.balas:
                        self.balas.remove(bala)
                    if enemigo in self.enemigos:
                        self.enemigos.remove(enemigo)
                    break
        
        if int(self.progreso) % 25 == 0 and int(self.progreso) > 0:
            self.texto = random.choice(self.mensajes_carga)
        
        self.progreso = min(100, self.progreso + random.uniform(0.5, 1.5))
        if self.progreso >= 100:
            self.cargando = False
    
    def dibujar(self, pantalla):
        pantalla.fill((0, 0, 20))
        for i, (x, y, speed) in enumerate(self.estrellas):
            y = (y + speed) % ALTO
            alpha = int(100 + 155 * (speed / 1.5))
            pygame.draw.circle(pantalla, (alpha, alpha, alpha), (x, y), 1)
            self.estrellas[i] = (x, y, speed)
        
        for enemigo in self.enemigos:
            pantalla.blit(pygame.transform.scale(roca_img, (40, 40)), enemigo)
        
        for bala in self.balas:
            pygame.draw.rect(pantalla, (50, 255, 100), bala)
            pygame.draw.rect(pantalla, (150, 255, 150), pygame.Rect(bala.x, bala.y, 4, 3))
        
        pantalla.blit(self.nave_img, self.nave_rect)
        
        barra_ancho = ANCHO // 2
        barra_x = ANCHO // 4
        barra_y = ALTO - 50
        
        pygame.draw.rect(pantalla, (0, 50, 100), (barra_x, barra_y, barra_ancho, 20), border_radius=10)
        pygame.draw.rect(pantalla, (0, 180, 255), (barra_x, barra_y, barra_ancho * (self.progreso / 100), 20), border_radius=10)
        pygame.draw.rect(pantalla, (0, 220, 255), (barra_x, barra_y, barra_ancho, 20), 2, border_radius=10)
        
        texto = fuente_carga.render(f"{self.texto} {int(self.progreso)}%", True, (255, 255, 255))
        pantalla.blit(texto, (ANCHO // 2 - texto.get_width() // 2, ALTO - 80))
        
        instrucciones = fuente_carga.render("Cargando...", True, (200, 200, 200))
        pantalla.blit(instrucciones, (ANCHO // 2 - instrucciones.get_width() // 2, 20))

class Nave:
    def __init__(self):
        self.aspectos = [
            Aspecto("Clásica", pygame.transform.scale(nave_img, (60, 60)), 0, True),
            Aspecto("Veloz", pygame.transform.scale(nave_img2, (60, 60)), 500),
            Aspecto("Pesada", pygame.transform.scale(nave_img3, (60, 60)), 1000),
            Aspecto("Cazadora", pygame.transform.scale(nave_img4, (60, 60)), 1500),
            Aspecto("Alienígena", pygame.transform.scale(nave_img5, (60, 60)), 2000)
        ]
        
        # Sistema de mejoras con imágenes
        self.mejoras = {
            "velocidad": Mejora("Velocidad", "Aumenta la velocidad de la nave", 200, imagen=velocidad_icon_img),
            "disparo": Mejora("Disparo", "Reduce el tiempo entre disparos", 300, imagen=disparo_icon_img),
            "vida": Mejora("Vida", "Aumenta la vida máxima", 500, 3, imagen=vida_icon_img)
        }
        
        self.aspecto_equipado = 0
        self.image = self.aspectos[self.aspecto_equipado].imagen
        self.rect = self.image.get_rect(center=(ANCHO // 2, ALTO - 60))
        self.vel = 5
        self.vida = 3
        self.vida_maxima = 3
        self.puntaje = 0
        self.puntaje_total = 0
        self.puntaje_maximo = 0
        self.cooldown = 0
        self.cooldown_base = 15
        self.invulnerable = 0
        self.parpadeo = 0
        self.visible = True

        # Power-ups
        self.doble_disparo_ticks = 0
        self.escudo_ticks = 0

        if getattr(sys, 'frozen', False):
            self.progreso_path = os.path.join(os.environ.get('APPDATA'), 'GalaxyCodeInvasion')
        else:
            self.progreso_path = os.path.dirname(os.path.abspath(__file__))

        os.makedirs(self.progreso_path, exist_ok=True)
        self.cargar_progreso()
        
        # Aplicar mejoras cargadas
        self.aplicar_mejoras()

    def aplicar_mejoras(self):
        # Aplicar mejoras de velocidad
        self.vel = 5 + (self.mejoras["velocidad"].nivel * 0.5)
        
        # Aplicar mejoras de disparo
        self.cooldown_base = max(5, 15 - (self.mejoras["disparo"].nivel * 2))
        
        # Aplicar mejoras de vida
        self.vida_maxima = 3 + self.mejoras["vida"].nivel
        self.vida = min(self.vida, self.vida_maxima)

    def comprar_mejora(self, tipo_mejora):
        mejora = self.mejoras[tipo_mejora]
        if mejora.nivel < mejora.nivel_max and self.puntaje_total >= mejora.precio_actual():
            self.puntaje_total -= mejora.precio_actual()
            mejora.mejorar()
            self.aplicar_mejoras()
            self.guardar_progreso()
            return True
        return False

    def comprar_aspecto(self, indice):
        aspecto = self.aspectos[indice]
        if not aspecto.desbloqueado and self.puntaje_total >= aspecto.precio:
            self.puntaje_total -= aspecto.precio
            aspecto.desbloqueado = True
            self.guardar_progreso()
            return True
        return False
    
    def cambiar_aspecto(self, indice):
        if self.aspectos[indice].desbloqueado:
            self.aspecto_equipado = indice
            self.image = self.aspectos[indice].imagen
            self.guardar_progreso()
            return True
        return False

    def agregar_puntos(self, puntos):
        self.puntaje += puntos
        self.puntaje_total += puntos
        if self.puntaje > self.puntaje_maximo:
            self.puntaje_maximo = self.puntaje
        self.guardar_progreso()

    def guardar_progreso(self):
        datos = {
            'puntaje_total': self.puntaje_total,
            'puntaje_maximo': self.puntaje_maximo,
            'aspectos': [
                {'nombre': a.nombre, 'precio': a.precio, 'desbloqueado': a.desbloqueado}
                for a in self.aspectos
            ],
            'aspecto_equipado': self.aspecto_equipado,
            'mejoras': {tipo: {'nivel': mejora.nivel} for tipo, mejora in self.mejoras.items()}
        }
        try:
            archivo_progreso = os.path.join(self.progreso_path, 'progreso.json')
            with open(archivo_progreso, 'w') as archivo:
                json.dump(datos, archivo)
        except Exception as e:
            print(f"Error al guardar progreso: {e}")

    def cargar_progreso(self):
        try:
            archivo_progreso = os.path.join(self.progreso_path, 'progreso.json')
            if os.path.exists(archivo_progreso):
                with open(archivo_progreso, 'r') as archivo:
                    datos = json.load(archivo)
                    self.puntaje_total = datos.get('puntaje_total', 0)
                    self.puntaje_maximo = datos.get('puntaje_maximo', 0)

                    aspectos_data = datos.get('aspectos', [])
                    for i, aspecto_data in enumerate(aspectos_data):
                        if i < len(self.aspectos):
                            self.aspectos[i].desbloqueado = aspecto_data.get('desbloqueado', False)

                    self.aspecto_equipado = datos.get('aspecto_equipado', 0)
                    self.image = self.aspectos[self.aspecto_equipado].imagen
                    
                    # Cargar mejoras
                    mejoras_data = datos.get('mejoras', {})
                    for tipo, mejora_data in mejoras_data.items():
                        if tipo in self.mejoras:
                            self.mejoras[tipo].nivel = mejora_data.get('nivel', 0)
        except Exception as e:
            print(f"Error al cargar progreso: {e}")

    def reiniciar_puntaje_partida(self):
        self.puntaje = 0

    def dibujar(self):
        # Halo de escudo si está activo
        if self.escudo_ticks > 0:
            pygame.draw.circle(PANTALLA, (0, 180, 255, 80), self.rect.center, 40, 2)
        if self.visible:
            PANTALLA.blit(self.image, self.rect)

    def mover(self, teclas):
        velocidad_actual = self.vel
        if (teclas[pygame.K_LEFT] or teclas[pygame.K_a]) and self.rect.left > 0:
            self.rect.x -= velocidad_actual
        if (teclas[pygame.K_RIGHT] or teclas[pygame.K_d]) and self.rect.right < ANCHO:
            self.rect.x += velocidad_actual
        if teclas[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= velocidad_actual
        if teclas[pygame.K_DOWN] and self.rect.bottom < ALTO:
            self.rect.y += velocidad_actual

    def disparar(self, balas):
        if self.cooldown == 0:
            # Disparo principal
            balas.append(Bala(self.rect.centerx, self.rect.top))
            # Doble disparo si power-up activo
            if self.doble_disparo_ticks > 0:
                balas.append(Bala(self.rect.centerx - 12, self.rect.top))
                balas.append(Bala(self.rect.centerx + 12, self.rect.top))
            self.cooldown = self.cooldown_base
            if sonido_disparo:
                sonido_disparo.play()

    def recibir_dano(self):
        # Si hay escudo, ignora el daño
        if self.escudo_ticks > 0:
            return
        self.vida -= 1
        self.invulnerable = 60
        self.parpadeo = 30

    def actualizar(self):
        if self.cooldown > 0:
            self.cooldown -= 1
        
        if self.invulnerable > 0:
            self.invulnerable -= 1
            self.parpadeo -= 1
            if self.parpadeo <= 0:
                self.parpadeo = 5
                self.visible = not self.visible
        else:
            self.visible = True

        # Reducir contadores de power-ups
        if self.doble_disparo_ticks > 0:
            self.doble_disparo_ticks -= 1
        if self.escudo_ticks > 0:
            self.escudo_ticks -= 1

    def aplicar_powerup(self, tipo):
        if tipo == "doble_disparo":
            self.doble_disparo_ticks = max(self.doble_disparo_ticks, 60 * 8)  # 8 s
        elif tipo == "escudo":
            self.escudo_ticks = max(self.escudo_ticks, 60 * 6)  # 6 s
        elif tipo == "vida":
            self.vida = min(self.vida + 1, self.vida_maxima)
        if sonido_powerup:
            sonido_powerup.play()

class Enemigo:
    def __init__(self):
        self.image = pygame.transform.scale(roca_img, (40, 40))
        self.rect = self.image.get_rect(
            center=(random.randint(20, ANCHO - 20), random.randint(-150, -40)))
        self.vel = random.uniform(1, 3)
        self.angulo = random.uniform(-0.5, 0.5)

    def dibujar(self):
        PANTALLA.blit(self.image, self.rect)

    def mover(self):
        self.rect.y += self.vel
        self.rect.x += math.sin(self.rect.y * self.angulo) * 2

class EnemigoEspecial:
    def __init__(self, tipo):
        self.tipo = tipo  # "veloz", "resistente", "kamikaze", "titan"
        self.vida = 2 if tipo != "titan" else 5
        self.puntos = 10 if tipo != "titan" else 50
        
        # Configuración según tipo
        if tipo == "veloz":
            self.image = pygame.transform.scale(nave_img2, (50, 50))
            self.vel = random.uniform(4, 6)
            self.color = (255, 100, 100)  # Rojo claro
        elif tipo == "resistente":
            self.image = pygame.transform.scale(nave_img3, (60, 60))
            self.vel = random.uniform(1, 2)
            self.color = (100, 100, 255)  # Azul claro
        elif tipo == "kamikaze":
            self.image = pygame.transform.scale(nave_img4, (45, 45))
            self.vel = random.uniform(3, 4)
            self.color = (255, 255, 100)  # Amarillo
        elif tipo == "titan":
            self.image = pygame.transform.scale(nave_img5, (80, 80))
            self.vel = random.uniform(0.5, 1.5)
            self.color = (150, 50, 150)  # Púrpura
            
        self.rect = self.image.get_rect(
            center=(random.randint(50, ANCHO-50), random.randint(-200, -100)))
        self.angulo = random.uniform(-0.3, 0.3)
        self.tiempo_disparo = 0
        self.disparos = [] if tipo in ["resistente", "titan"] else None
        self.tiempo_invulnerable = 0
        
    def dibujar(self):
        # Dibujar halo de color según tipo
        if self.tipo in ["titan", "resistente"]:
            overlay = pygame.Surface((self.rect.width + 10, self.rect.height + 10), pygame.SRCALPHA)
            pygame.draw.circle(overlay, (*self.color[:3], 50), (overlay.get_width()//2, overlay.get_height()//2), 
                              overlay.get_width()//2)
            PANTALLA.blit(overlay, (self.rect.x-5, self.rect.y-5))
        
        PANTALLA.blit(self.image, self.rect)
        
        # Barra de vida para enemigos especiales
        vida_max = 2 if self.tipo != "titan" else 5
        if self.vida < vida_max:
            barra_ancho = self.rect.width * (self.vida / vida_max)
            pygame.draw.rect(PANTALLA, (255, 0, 0), (self.rect.left, self.rect.top - 10, 
                                                    self.rect.width, 3))
            pygame.draw.rect(PANTALLA, (0, 255, 0), (self.rect.left, self.rect.top - 10, 
                                                    barra_ancho, 3))
    
    def mover(self, nave):
        if self.tiempo_invulnerable > 0:
            self.tiempo_invulnerable -= 1
            
        self.rect.y += self.vel
        self.rect.x += math.sin(self.rect.y * self.angulo) * 2
        
        # Comportamientos especiales
        if self.tipo == "kamikaze" and self.rect.y > ALTO//4:
            # Perseguir al jugador
            if nave.rect.centerx < self.rect.centerx:
                self.rect.x -= 1.5
            elif nave.rect.centerx > self.rect.centerx:
                self.rect.x += 1.5
        
        if self.tipo in ["resistente", "titan"]:
            self.tiempo_disparo += 1
            if self.tiempo_disparo > 90:  # Disparar cada 1.5 segundos
                self.disparos.append(Bala(self.rect.centerx, self.rect.bottom, 
                                       velocidad=4, es_enemiga=True))
                self.tiempo_disparo = 0
                if sonido_disparo_enemigo:
                    sonido_disparo_enemigo.play()
    
    def actualizar_disparos(self):
        if self.disparos:
            for disparo in self.disparos[:]:
                disparo.mover()
                if disparo.rect.top > ALTO:
                    self.disparos.remove(disparo)
    
    def dibujar_disparos(self):
        if self.disparos:
            for disparo in self.disparos:
                disparo.dibujar()

class Bala:
    def __init__(self, x, y, velocidad=8, es_enemiga=False):
        self.rect = pygame.Rect(x - 2, y, 4, 10)
        self.vel = velocidad
        self.es_enemiga = es_enemiga
        self.trail_particles = []
    
    def dibujar(self):
        if random.random() < 0.5:
            color = (255, 100, 100) if self.es_enemiga else (100, 255, 150)
            pos_y = self.rect.bottom if self.es_enemiga else self.rect.top
            self.trail_particles.append(Particula(
                self.rect.centerx, pos_y,
                color,
                size=random.randint(1, 2),
                speed=random.uniform(0.1, 0.5),
                angle=math.pi/2 if self.es_enemiga else -math.pi/2,
                life=random.randint(5, 10))
            )
        
        self.trail_particles = [p for p in self.trail_particles if p.update()]
        for p in self.trail_particles:
            p.draw(PANTALLA)
        
        if self.es_enemiga:
            pygame.draw.rect(PANTALLA, (255, 50, 50), self.rect)
            pygame.draw.rect(PANTALLA, (255, 150, 150), pygame.Rect(self.rect.x, self.rect.y, 4, 3))
        else:
            pygame.draw.rect(PANTALLA, (50, 255, 100), self.rect)
            pygame.draw.rect(PANTALLA, (200, 255, 220), pygame.Rect(self.rect.x, self.rect.y, 4, 3))
            pygame.draw.rect(PANTALLA, (255, 255, 255), pygame.Rect(self.rect.x+1, self.rect.y, 2, 2))

    def mover(self):
        if self.es_enemiga:
            self.rect.y += self.vel
        else:
            self.rect.y -= self.vel

class PowerUp:
    def __init__(self, x, y, tipo):
        self.tipo = tipo  # "doble_disparo", "escudo", "vida"
        self.vel = 2.5
        self.size = 28
        # Selección de imagen
        if self.tipo == "doble_disparo":
            base = power_doble_img
            color = (0, 255, 0)
        elif self.tipo == "escudo":
            base = power_escudo_img
            color = (0, 180, 255)
        else:
            base = power_vida_img
            color = (255, 80, 80)

        # Si la imagen existe, escalar; si no, crear placeholder
        if base is not None:
            self.image = pygame.transform.scale(base, (self.size, self.size))
        else:
            surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.circle(surf, color, (self.size // 2, self.size // 2), self.size // 2, 2)
            pygame.draw.circle(surf, (255, 255, 255), (self.size // 2, self.size // 2), 4)
            self.image = surf

        self.rect = self.image.get_rect(center=(x, y))

    def mover(self):
        self.rect.y += self.vel

    def dibujar(self):
        PANTALLA.blit(self.image, self.rect)

def colision(rect1, rect2):
    return rect1.colliderect(rect2)

def mostrar_texto(texto, x, y, color=(255, 255, 255), tam=28, centrado=False):
    try:
        fuente_temp = pygame.font.SysFont("consolas", tam)
    except:
        fuente_temp = pygame.font.Font(None, tam)
    render = fuente_temp.render(texto, True, color)
    if centrado:
        rect = render.get_rect(center=(x, y))
        PANTALLA.blit(render, rect)
    else:
        PANTALLA.blit(render, (x, y))

def mostrar_texto_sombra(texto, x, y, color=(255, 255, 255), sombra=(0, 0, 0), tam=28, centrado=False):
    mostrar_texto(texto, x+2, y+2, sombra, tam, centrado)
    mostrar_texto(texto, x, y, color, tam, centrado)

def tienda(nave):
    global pantalla_completa, PANTALLA, ANCHO, ALTO

    opciones = ["COMPRAR ASPECTOS", "EQUIPAR ASPECTOS", "MEJORAR NAVE", "VOLVER"]
    seleccion = 0
    subseleccion = 0
    modo = "principal"
    ejecutando = True
    mensaje = ""
    tiempo_mensaje = 0

    while ejecutando:
        PANTALLA.blit(fondo_img, (0, 0))

        for _ in range(2):
            pygame.draw.circle(PANTALLA, (random.randint(100, 255), random.randint(100, 255), 255),
                              (random.randint(0, ANCHO), random.randint(0, ALTO)), 1)

        titulo_surf = fuente_titulo.render("TIENDA GALÁCTICA", True, (0, 180, 255))
        titulo_rect = titulo_surf.get_rect(center=(ANCHO//2, 50))
        PANTALLA.blit(titulo_surf, titulo_rect)

        mostrar_texto_sombra(f"PUNTOS: {nave.puntaje_total}", ANCHO//2 - 100, 100, (255, 255, 0), (0, 0, 0))

        if tiempo_mensaje > 0:
            mostrar_texto_sombra(mensaje, ANCHO//2, ALTO - 100, (255, 255, 255), (0, 0, 0), 24, True)
            tiempo_mensaje -= 1

        if modo == "principal":
            for i, texto in enumerate(opciones):
                color = (255, 255, 255) if i == seleccion else (150, 150, 150)
                opcion_surf = fuente.render(texto, True, color)
                opcion_rect = opcion_surf.get_rect(center=(ANCHO//2, 200 + i * 60))

                if i == seleccion:
                    pygame.draw.rect(PANTALLA, (0, 180, 255, 100), opcion_rect.inflate(20, 10), border_radius=5)
                    pygame.draw.rect(PANTALLA, (0, 220, 255), opcion_rect.inflate(20, 10), 2, border_radius=5)

                PANTALLA.blit(opcion_surf, opcion_rect)

        elif modo == "comprar":
            mostrar_texto_sombra("SELECCIONA UN ASPECTO PARA COMPRAR", ANCHO//2, 150, (255, 255, 255), (0, 0, 0), 24, True)

            for i, aspecto in enumerate(nave.aspectos):
                if aspecto.desbloqueado:
                    color = (0, 255, 0)
                    texto = f"{aspecto.nombre} - COMPRADO"
                else:
                    if i == subseleccion:
                        color = (255, 255, 255)
                    else:
                        color = (100, 100, 100)
                    texto = f"{aspecto.nombre} - {aspecto.precio} pts (BLOQUEADO)"

                aspecto_surf = fuente.render(texto, True, color)
                aspecto_rect = aspecto_surf.get_rect(center=(ANCHO//2, 220 + i * 80))

                if i == subseleccion:
                    pygame.draw.rect(PANTALLA, (0, 180, 255, 100), aspecto_rect.inflate(20, 10), border_radius=5)
                    pygame.draw.rect(PANTALLA, (0, 220, 255), aspecto_rect.inflate(20, 10), 2, border_radius=5)

                miniatura = pygame.transform.scale(aspecto.imagen, (80, 80))
                PANTALLA.blit(miniatura, (ANCHO//2 - 200, 200 + i * 80))

                if not aspecto.desbloqueado:
                    overlay = pygame.Surface((80, 80), pygame.SRCALPHA)
                    overlay.fill((0, 0, 0, 180))
                    PANTALLA.blit(overlay, (ANCHO//2 - 200, 200 + i * 80))
                    candado = pygame.Surface((80, 80), pygame.SRCALPHA)
                    pygame.draw.rect(candado, (150, 150, 150), (30, 30, 20, 30), 3)
                    pygame.draw.rect(candado, (150, 150, 150), (34, 15, 12, 15), 3)
                    PANTALLA.blit(candado, (ANCHO//2 - 200, 200 + i * 80))

                PANTALLA.blit(aspecto_surf, aspecto_rect)

        elif modo == "equipar":
            mostrar_texto_sombra("SELECCIONA UN ASPECTO PARA EQUIPAR", ANCHO//2, 150, (255, 255, 255), (0, 0, 0), 24, True)

            for i, aspecto in enumerate(nave.aspectos):
                if aspecto.desbloqueado:
                    color = (0, 255, 255) if i == nave.aspecto_equipado else ((255, 255, 255) if i == subseleccion else (150, 150, 150))
                    texto = f"{aspecto.nombre}"
                    if i == nave.aspecto_equipado:
                        texto += " (EQUIPADO)"
                else:
                    color = (100, 100, 100)
                    texto = f"{aspecto.nombre} (BLOQUEADO)"

                aspecto_surf = fuente.render(texto, True, color)
                aspecto_rect = aspecto_surf.get_rect(center=(ANCHO//2, 220 + i * 80))

                if i == subseleccion and aspecto.desbloqueado:
                    pygame.draw.rect(PANTALLA, (0, 180, 255, 100), aspecto_rect.inflate(20, 10), border_radius=5)
                    pygame.draw.rect(PANTALLA, (0, 220, 255), aspecto_rect.inflate(20, 10), 2, border_radius=5)

                miniatura = pygame.transform.scale(aspecto.imagen, (80, 80))
                PANTALLA.blit(miniatura, (ANCHO//2 - 200, 200 + i * 80))

                if not aspecto.desbloqueado:
                    overlay = pygame.Surface((80, 80), pygame.SRCALPHA)
                    overlay.fill((0, 0, 0, 180))
                    PANTALLA.blit(overlay, (ANCHO//2 - 200, 200 + i * 80))
                    candado = pygame.Surface((80, 80), pygame.SRCALPHA)
                    pygame.draw.rect(candado, (150, 150, 150), (30, 30, 20, 30), 3)
                    pygame.draw.rect(candado, (150, 150, 150), (34, 15, 12, 15), 3)
                    PANTALLA.blit(candado, (ANCHO//2 - 200, 200 + i * 80))

                PANTALLA.blit(aspecto_surf, aspecto_rect)

        elif modo == "mejorar":
            mostrar_texto_sombra("SELECCIONA UNA MEJORA", ANCHO//2, 150, (255, 255, 255), (0, 0, 0), 24, True)

            tipos_mejoras = list(nave.mejoras.keys())
            for i, tipo in enumerate(tipos_mejoras):
                mejora = nave.mejoras[tipo]
                
                if mejora.nivel < mejora.nivel_max:
                    color = (255, 255, 255) if i == subseleccion else (150, 150, 150)
                    texto = f"{mejora.nombre} (Nv. {mejora.nivel+1}/{mejora.nivel_max}) - {mejora.precio_actual()} pts"
                else:
                    color = (0, 255, 0)
                    texto = f"{mejora.nombre} (Nv. MAX)"

                mejora_surf = fuente.render(texto, True, color)
                mejora_rect = mejora_surf.get_rect(center=(ANCHO//2, 220 + i * 80))

                if i == subseleccion and mejora.nivel < mejora.nivel_max:
                    pygame.draw.rect(PANTALLA, (0, 180, 255, 100), mejora_rect.inflate(20, 10), border_radius=5)
                    pygame.draw.rect(PANTALLA, (0, 220, 255), mejora_rect.inflate(20, 10), 2, border_radius=5)

                # Dibujar icono de mejora
                icono_rect = pygame.Rect(ANCHO//2 - 200, 200 + i * 80, 80, 80)
                
                if mejora.imagen:
                    # Si hay imagen, mostrarla
                    icono_escalado = pygame.transform.scale(mejora.imagen, (60, 60))
                    PANTALLA.blit(icono_escalado, (ANCHO//2 - 190, 210 + i * 80))
                else:
                    # Si no hay imagen, dibujar placeholder
                    pygame.draw.rect(PANTALLA, (50, 50, 50), icono_rect)
                    pygame.draw.rect(PANTALLA, (100, 100, 100), icono_rect, 2)
                
                # Dibujar barra de nivel
                nivel_rect = pygame.Rect(ANCHO//2 - 200, 285 + i * 80, 80, 5)
                pygame.draw.rect(PANTALLA, (50, 50, 50), nivel_rect)
                if mejora.nivel > 0:
                    nivel_width = (80 * mejora.nivel) // mejora.nivel_max
                    pygame.draw.rect(PANTALLA, (0, 200, 0), pygame.Rect(ANCHO//2 - 200, 285 + i * 80, nivel_width, 5))

                PANTALLA.blit(mejora_surf, mejora_rect)

        volver_color = (200, 200, 200) if pygame.time.get_ticks() % 1000 < 500 else (255, 255, 255)
        volver_surf = fuente.render("VOLVER (ESC)", True, volver_color)
        PANTALLA.blit(volver_surf, (20, ALTO - 40))

        pygame.display.update()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    if modo != "principal":
                        modo = "principal"
                    else:
                        ejecutando = False
                elif evento.key == pygame.K_UP:
                    if modo == "principal":
                        seleccion = (seleccion - 1) % len(opciones)
                    else:
                        if modo == "equipar":
                            nueva_seleccion = subseleccion
                            for _ in range(len(nave.aspectos)):
                                nueva_seleccion = (nueva_seleccion - 1) % len(nave.aspectos)
                                if nave.aspectos[nueva_seleccion].desbloqueado or modo == "comprar":
                                    break
                            subseleccion = nueva_seleccion
                        elif modo == "mejorar":
                            subseleccion = (subseleccion - 1) % len(nave.mejoras)
                        else:
                            subseleccion = (subseleccion - 1) % len(nave.aspectos)
                elif evento.key == pygame.K_DOWN:
                    if modo == "principal":
                        seleccion = (seleccion + 1) % len(opciones)
                    else:
                        if modo == "equipar":
                            nueva_seleccion = subseleccion
                            for _ in range(len(nave.aspectos)):
                                nueva_seleccion = (nueva_seleccion + 1) % len(nave.aspectos)
                                if nave.aspectos[nueva_seleccion].desbloqueado or modo == "comprar":
                                    break
                            subseleccion = nueva_seleccion
                        elif modo == "mejorar":
                            subseleccion = (subseleccion + 1) % len(nave.mejoras)
                        else:
                            subseleccion = (subseleccion + 1) % len(nave.aspectos)
                elif evento.key == pygame.K_RETURN:
                    if modo == "principal":
                        if seleccion == 0:
                            modo = "comprar"
                            for i, aspecto in enumerate(nave.aspectos):
                                if not aspecto.desbloqueado:
                                    subseleccion = i
                                    break
                        elif seleccion == 1:
                            modo = "equipar"
                            subseleccion = nave.aspecto_equipado
                        elif seleccion == 2:
                            modo = "mejorar"
                            subseleccion = 0
                        elif seleccion == 3:
                            ejecutando = False
                    elif modo == "comprar":
                        if not nave.aspectos[subseleccion].desbloqueado:
                            if nave.comprar_aspecto(subseleccion):
                                mensaje = f"¡{nave.aspectos[subseleccion].nombre} comprado!"
                                tiempo_mensaje = 60
                            else:
                                mensaje = "¡Puntos insuficientes!"
                                tiempo_mensaje = 60
                    elif modo == "equipar":
                        if nave.aspectos[subseleccion].desbloqueado:
                            if nave.cambiar_aspecto(subseleccion):
                                mensaje = f"¡{nave.aspectos[subseleccion].nombre} equipado!"
                                tiempo_mensaje = 60
                    elif modo == "mejorar":
                        tipos_mejoras = list(nave.mejoras.keys())
                        tipo = tipos_mejoras[subseleccion]
                        if nave.mejoras[tipo].nivel < nave.mejoras[tipo].nivel_max:
                            if nave.comprar_mejora(tipo):
                                mensaje = f"¡{nave.mejoras[tipo].nombre} mejorada a nivel {nave.mejoras[tipo].nivel}!"
                                tiempo_mensaje = 60
                            else:
                                mensaje = "¡Puntos insuficientes!"
                                tiempo_mensaje = 60
                        else:
                            mensaje = "¡Mejora al máximo nivel!"
                            tiempo_mensaje = 60
                elif evento.key == pygame.K_F11:
                    pantalla_completa = not pantalla_completa
                    if pantalla_completa:
                        PANTALLA = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                        ANCHO, ALTO = PANTALLA.get_size()
                    else:
                        PANTALLA = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
                        ANCHO, ALTO = 800, 600
            elif evento.type == pygame.VIDEORESIZE and not pantalla_completa:
                ANCHO, ALTO = evento.w, evento.h
                PANTALLA = pygame.display.set_mode((ANCHO, ALTO), pygame.RESIZABLE)

        RELOJ.tick(60)

def mostrar_game_over(nave):
    global pantalla_completa, PANTALLA, ANCHO, ALTO
    
    if sonido_game_over:
        sonido_game_over.play()
    opciones = ["Volver a jugar", "Menú principal", "Salir del juego"]
    seleccion = 0
    alpha = 0
    fade_speed = 5
    ejecutando = True
    
    overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    explosiones = [Explosion(random.randint(100, ANCHO-100), random.randint(100, ALTO-100)) for _ in range(3)]
    
    while ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_UP:
                    seleccion = (seleccion - 1) % len(opciones)
                elif evento.key == pygame.K_DOWN:
                    seleccion = (seleccion + 1) % len(opciones)
                elif evento.key == pygame.K_RETURN:
                    if seleccion == 0:
                        return "restart"
                    elif seleccion == 1:
                        return "menu"
                    elif seleccion == 2:
                        pygame.quit()
                        sys.exit()
                elif evento.key == pygame.K_ESCAPE:
                    return "menu"
                elif evento.key == pygame.K_F11:
                    pantalla_completa = not pantalla_completa
                    if pantalla_completa:
                        PANTALLA = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                        ANCHO, ALTO = PANTALLA.get_size()
                    else:
                        PANTALLA = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
                        ANCHO, ALTO = 800, 600
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1:
                    if seleccion == 0:
                        return "restart"
                    elif seleccion == 1:
                        return "menu"
                    elif seleccion == 2:
                        pygame.quit()
                        sys.exit()
        
        explosiones = [e for e in explosiones if e.update()]
        if random.random() < 0.05 and len(explosiones) < 5:
            explosiones.append(Explosion(random.randint(100, ANCHO-100), random.randint(100, ALTO-100)))
        
        for explosion in explosiones:
            explosion.draw(PANTALLA)
        
        if alpha < 180:
            alpha += fade_speed
        
        overlay.fill((0, 0, 0, alpha))
        PANTALLA.blit(overlay, (0, 0))
        
        img_alpha = min(255, alpha * 1.5)
        game_over_img.set_alpha(img_alpha)
        img_rect = game_over_img.get_rect(center=(ANCHO//2, ALTO//2 - 100))
        PANTALLA.blit(game_over_img, img_rect)
        
        mostrar_texto_sombra(f"Puntuación: {nave.puntaje}", ANCHO//2, ALTO//2 - 20, (255, 255, 255), (0, 0, 0), 32, True)
        mostrar_texto_sombra(f"Récord: {max(nave.puntaje, nave.puntaje_maximo)}", ANCHO//2, ALTO//2 + 20, (255, 255, 0), (0, 0, 0), 32, True)
        
        for i, opcion in enumerate(opciones):
            color = (0, 180, 255) if i == seleccion else (200, 200, 200)
            opcion_surf = fuente.render(opcion, True, color)
            opcion_rect = opcion_surf.get_rect(center=(ANCHO//2, ALTO//2 + 100 + i * 50))
            
            if i == seleccion:
                pygame.draw.rect(PANTALLA, (0, 180, 255, 50), opcion_rect.inflate(20, 10), border_radius=5)
                pygame.draw.rect(PANTALLA, (0, 220, 255), opcion_rect.inflate(20, 10), 2, border_radius=5)
            
            PANTALLA.blit(opcion_surf, opcion_rect)
        
        pygame.display.update()
        RELOJ.tick(60)

def menu():
    global pantalla_completa, PANTALLA, ANCHO, ALTO
    
    opciones = ["INICIAR JUEGO", "TIENDA", "SALIR"]
    seleccion = 0
    ejecutando = True
    if sonido_menu:
        sonido_menu.play(-1)
    nave = Nave()
    
    estrellas = [(random.randint(0, ANCHO), random.randint(0, ALTO), random.uniform(0.5, 1.5)) for _ in range(100)]

    while ejecutando:
        PANTALLA.blit(fondo_img, (0, 0))
        
        for x, y, speed in estrellas:
            alpha = int((math.sin(pygame.time.get_ticks() * 0.001 * speed) + 1) * 100 + 55)
            color = (alpha, alpha, alpha)
            pygame.draw.circle(PANTALLA, color, (x, y), 1)

        titulo_surf = fuente_titulo.render("GALAXY CODE: INVASION", True, (0, 180, 255))
        titulo_rect = titulo_surf.get_rect(center=(ANCHO//2, 100))
        
        if pygame.time.get_ticks() % 2000 < 1000:
            highlight = pygame.Surface((titulo_surf.get_width()+20, titulo_surf.get_height()+20), pygame.SRCALPHA)
            pygame.draw.rect(highlight, (0, 180, 255, 30), highlight.get_rect(), border_radius=10)
            PANTALLA.blit(highlight, (titulo_rect.x-10, titulo_rect.y-10))
        
        PANTALLA.blit(titulo_surf, titulo_rect)

        for i, texto in enumerate(opciones):
            color = (255, 255, 255) if i == seleccion else (150, 150, 150)
            opcion_surf = fuente.render(texto, True, color)
            opcion_rect = opcion_surf.get_rect(center=(ANCHO//2, 250 + i * 60))

            if i == seleccion:
                pygame.draw.rect(PANTALLA, (0, 180, 255, 100), opcion_rect.inflate(20, 10), border_radius=5)
                pygame.draw.rect(PANTALLA, (0, 220, 255), opcion_rect.inflate(20, 10), 2, border_radius=5)
            
            PANTALLA.blit(opcion_surf, opcion_rect)

        mostrar_texto_sombra(f"Récord: {nave.puntaje_maximo}", ANCHO//2, ALTO - 50, (255, 255, 0), (0, 0, 0), 24, True)

        pygame.display.update()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_UP:
                    seleccion = (seleccion - 1) % len(opciones)
                    if sonido_menu:
                        sonido_menu.stop()
                        sonido_menu.play()
                elif evento.key == pygame.K_DOWN:
                    seleccion = (seleccion + 1) % len(opciones)
                    if sonido_menu:
                        sonido_menu.stop()
                        sonido_menu.play()
                elif evento.key == pygame.K_RETURN:
                    if sonido_menu:
                        sonido_menu.stop()
                    if seleccion == 0:
                        return
                    elif seleccion == 1:
                        tienda(nave)
                        if sonido_menu:
                            sonido_menu.play(-1)
                    elif seleccion == 2:
                        pygame.quit()
                        sys.exit()
                elif evento.key == pygame.K_F11:
                    pantalla_completa = not pantalla_completa
                    if pantalla_completa:
                        PANTALLA = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                        ANCHO, ALTO = PANTALLA.get_size()
                    else:
                        PANTALLA = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
                        ANCHO, ALTO = 800, 600
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1:
                    if seleccion == 0:
                        return
                    elif seleccion == 1:
                        tienda(nave)
                        if sonido_menu:
                            sonido_menu.play(-1)
                    elif seleccion == 2:
                        pygame.quit()
                        sys.exit()
            elif evento.type == pygame.VIDEORESIZE and not pantalla_completa:
                ANCHO, ALTO = evento.w, evento.h
                PANTALLA = pygame.display.set_mode((ANCHO, ALTO), pygame.RESIZABLE)

        RELOJ.tick(60)

def mostrar_pantalla_carga(mensaje="Cargando recursos..."):
    pantalla_carga = PantallaCarga(mensaje)
    while pantalla_carga.cargando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif evento.key == pygame.K_F11:
                    global pantalla_completa, PANTALLA, ANCHO, ALTO
                    pantalla_completa = not pantalla_completa
                    if pantalla_completa:
                        PANTALLA = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                        ANCHO, ALTO = PANTALLA.get_size()
                    else:
                        PANTALLA = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
                        ANCHO, ALTO = 800, 600
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1:
                    pass
            elif evento.type == pygame.VIDEORESIZE and not pantalla_completa:
                ANCHO, ALTO = evento.w, evento.h
                PANTALLA = pygame.display.set_mode((ANCHO, ALTO), pygame.RESIZABLE)
        
        pantalla_carga.actualizar()
        pantalla_carga.dibujar(PANTALLA)
        pygame.display.flip()
        RELOJ.tick(60)

def mostrar_pausa():
    global pantalla_completa, PANTALLA, ANCHO, ALTO
    
    opciones = ["Continuar", "Volver al menú", "Salir del juego"]
    seleccion = 0
    ejecutando = True
    
    # Crear overlay semitransparente
    overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    PANTALLA.blit(overlay, (0, 0))
    
    while ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_UP:
                    seleccion = (seleccion - 1) % len(opciones)
                elif evento.key == pygame.K_DOWN:
                    seleccion = (seleccion + 1) % len(opciones)
                elif evento.key == pygame.K_RETURN:
                    if seleccion == 0:
                        return "continuar"
                    elif seleccion == 1:
                        return "menu"
                    elif seleccion == 2:
                        pygame.quit()
                        sys.exit()
                elif evento.key == pygame.K_ESCAPE:
                    return "continuar"
                elif evento.key == pygame.K_F11:
                    pantalla_completa = not pantalla_completa
                    if pantalla_completa:
                        PANTALLA = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                        ANCHO, ALTO = PANTALLA.get_size()
                    else:
                        PANTALLA = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
                        ANCHO, ALTO = 800, 600
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1:
                    if seleccion == 0:
                        return "continuar"
                    elif seleccion == 1:
                        return "menu"
                    elif seleccion == 2:
                        pygame.quit()
                        sys.exit()
            elif evento.type == pygame.VIDEORESIZE and not pantalla_completa:
                ANCHO, ALTO = evento.w, evento.h
                PANTALLA = pygame.display.set_mode((ANCHO, ALTO), pygame.RESIZABLE)
        
        # Dibujar menú de pausa
        mostrar_texto_sombra("PAUSA", ANCHO//2, ALTO//2 - 100, (255, 255, 255), (0, 0, 0), 48, True)
        
        for i, opcion in enumerate(opciones):
            color = (0, 180, 255) if i == seleccion else (200, 200, 200)
            opcion_surf = fuente.render(opcion, True, color)
            opcion_rect = opcion_surf.get_rect(center=(ANCHO//2, ALTO//2 - 20 + i * 60))
            
            if i == seleccion:
                pygame.draw.rect(PANTALLA, (0, 180, 255, 50), opcion_rect.inflate(20, 10), border_radius=5)
                pygame.draw.rect(PANTALLA, (0, 220, 255), opcion_rect.inflate(20, 10), 2, border_radius=5)
            
            PANTALLA.blit(opcion_surf, opcion_rect)
        
        pygame.display.update()
        RELOJ.tick(60)

# Sistema de consola para depuración
class Consola:
    def __init__(self):
        self.lineas = []
        self.visible = False
        self.input_text = ""
        self.historial = []
        self.indice_historial = 0
    
    def toggle(self):
        self.visible = not self.visible
        if self.visible:
            self.input_text = ""
    
    def agregar_linea(self, texto):
        self.lineas.append(texto)
        if len(self.lineas) > 10:
            self.lineas.pop(0)
    
    def procesar_comando(self, comando):
        self.agregar_linea(f"> {comando}")
        self.historial.append(comando)
        self.indice_historial = len(self.historial)
        
        partes = comando.split()
        if not partes:
            return
        
        comando = partes[0].lower()
        
        if comando == "help":
            self.agregar_linea("Comandos disponibles:")
            self.agregar_linea("  help - Muestra esta ayuda")
            self.agregar_linea("  clear - Limpia la consola")
            self.agregar_linea("  add_points <cantidad> - Añade puntos")
            self.agregar_linea("  god_mode - Activa/desactiva modo invencible")
            self.agregar_linea("  fps - Muestra/establece FPS")
        elif comando == "clear":
            self.lineas = []
        elif comando == "add_points" and len(partes) > 1:
            try:
                puntos = int(partes[1])
                return {"accion": "add_points", "puntos": puntos}
            except ValueError:
                self.agregar_linea("Error: Cantidad debe ser un número")
        elif comando == "god_mode":
            return {"accion": "god_mode"}
        elif comando == "fpc":
            if len(partes) > 1:
                try:
                    fps = int(partes[1])
                    return {"accion": "set_fps", "fps": fps}
                except ValueError:
                    self.agregar_linea("Error: FPS debe ser un número")
            else:
                return {"accion": "get_fps"}
        else:
            self.agregar_linea(f"Comando desconocido: {comando}")
        
        return None
    
    def dibujar(self, superficie):
        if not self.visible:
            return
        
        # Fondo de la consola
        console_height = 300
        console_rect = pygame.Rect(0, ALTO - console_height, ANCHO, console_height)
        pygame.draw.rect(superficie, (0, 0, 0, 200), console_rect)
        pygame.draw.rect(superficie, (0, 180, 255), console_rect, 2)
        
        # Líneas de texto
        y = ALTO - console_height + 10
        for linea in self.lineas:
            texto = fuente_pequena.render(linea, True, (200, 200, 200))
            superficie.blit(texto, (10, y))
            y += 20
        
        # Línea de entrada
        input_rect = pygame.Rect(0, ALTO - 30, ANCHO, 30)
        pygame.draw.rect(superficie, (30, 30, 30), input_rect)
        pygame.draw.rect(superficie, (0, 180, 255), input_rect, 1)
        
        prompt = fuente_pequena.render("> " + self.input_text, True, (255, 255, 255))
        superficie.blit(prompt, (10, ALTO - 25))

def main():
    global pantalla_completa, PANTALLA, ANCHO, ALTO
    
    mostrar_pantalla_carga("Preparando partida...")
    
    nave = Nave()
    enemigos = []
    balas = []
    powerups = []
    contador = 0
    FPS = 60
    ejecutando = True
    game_over = False
    explosiones = []
    particulas_impacto = []
    particulas_impulso = []
    fondo = FondoParallax()
    
    # Consola de depuración
    consola = Consola()
    god_mode = False

    # Dificultad dinámica
    spawn_interval_base = 30
    spawn_timer = 0

    # Enemigos especiales
    siguiente_enemigo_especial = 100  # Aparece el primer especial a los 100 puntos
    tiempo_anuncio_especial = 0
    mensaje_especial = ""
    
    # Pausa
    pausado = False

    while ejecutando:
        RELOJ.tick(FPS)
        
        # Eventos
        teclas = pygame.key.get_pressed()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_p and not consola.visible:
                    pausado = not pausado
                if evento.key == pygame.K_BACKQUOTE:  # Tecla ~
                    consola.toggle()
                if not game_over and not pausado and not consola.visible:
                    if evento.key == pygame.K_SPACE:
                        nave.disparar(balas)
                if consola.visible:
                    if evento.key == pygame.K_RETURN:
                        resultado = consola.procesar_comando(consola.input_text)
                        if resultado:
                            if resultado.get("accion") == "add_points":
                                nave.agregar_puntos(resultado["puntos"])
                            elif resultado.get("accion") == "god_mode":
                                god_mode = not god_mode
                                consola.agregar_linea(f"God mode: {'activado' if god_mode else 'desactivado'}")
                            elif resultado.get("accion") == "set_fps":
                                FPS = resultado["fps"]
                                consola.agregar_linea(f"FPS establecidos a: {FPS}")
                            elif resultado.get("accion") == "get_fps":
                                consola.agregar_linea(f"FPS actuales: {FPS}")
                        consola.input_text = ""
                    elif evento.key == pygame.K_BACKSPACE:
                        consola.input_text = consola.input_text[:-1]
                    elif evento.key == pygame.K_UP:
                        if consola.historial and consola.indice_historial > 0:
                            consola.indice_historial -= 1
                            consola.input_text = consola.historial[consola.indice_historial]
                    elif evento.key == pygame.K_DOWN:
                        if consola.historial and consola.indice_historial < len(consola.historial) - 1:
                            consola.indice_historial += 1
                            consola.input_text = consola.historial[consola.indice_historial]
                        else:
                            consola.input_text = ""
                    else:
                        if evento.unicode and len(evento.unicode) == 1:
                            consola.input_text += evento.unicode
                if evento.key == pygame.K_F11:
                    pantalla_completa = not pantalla_completa
                    if pantalla_completa:
                        PANTALLA = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                        ANCHO, ALTO = PANTALLA.get_size()
                    else:
                        PANTALLA = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
                        ANCHO, ALTO = 800, 600
            elif evento.type == pygame.MOUSEBUTTONDOWN and not game_over and not pausado and not consola.visible:
                if evento.button == 1:
                    nave.disparar(balas)
            elif evento.type == pygame.VIDEORESIZE and not pantalla_completa:
                ANCHO, ALTO = evento.w, evento.h
                PANTALLA = pygame.display.set_mode((ANCHO, ALTO), pygame.RESIZABLE)

        # Dibujo de fondo siempre
        fondo.actualizar()
        fondo.dibujar(PANTALLA)

        if pausado:
            resultado = mostrar_pausa()
            if resultado == "menu":
                return "menu"
            elif resultado == "continuar":
                pausado = False
            continue

        if consola.visible:
            # Si la consola está visible, no procesar el juego
            consola.dibujar(PANTALLA)
            pygame.display.update()
            continue

        if not game_over:
            nave.mover(teclas)
            nave.actualizar()

            # Spawning con dificultad dinámica
            dificultad = min(20, nave.puntaje // 5)  # escala con puntaje
            spawn_interval = max(10, spawn_interval_base - dificultad)
            spawn_timer += 1
            if spawn_timer >= spawn_interval:
                enemigos.append(Enemigo())
                spawn_timer = 0

            # Verificar si es momento de spawnear un enemigo especial
            if nave.puntaje >= siguiente_enemigo_especial:
                tipos = ["veloz", "resistente", "kamikaze"]
                if nave.puntaje >= 100:  # A partir de 500 puntos puede aparecer el titán
                    tipos.append("titan")
                
                tipo_elegido = random.choice(tipos)
                enemigos.append(EnemigoEspecial(tipo_elegido))
                
                # Mostrar mensaje de enemigo especial
                nombres_enemigos = {
                    "veloz": "ENEMIGO VELOZ",
                    "resistente": "ENEMIGO RESISTENTE",
                    "kamikaze": "KAMIKAZE",
                    "titan": "TITÁN"
                }
                mensaje_especial = f"¡{nombres_enemigos[tipo_elegido]} APARECIÓ! +{10 if tipo_elegido != 'titan' else 50} PUNTOS"
                tiempo_anuncio_especial = 120  # 2 segundos
                
                # Reproducir sonido especial
                if sonido_enemigo_especial:
                    sonido_enemigo_especial.play()
                
                # Establecer el próximo punto de aparición (entre 50 y 150 puntos más)
                siguiente_enemigo_especial += random.randint(35, 100)

            # Actualizar tiempo de anuncio especial
            if tiempo_anuncio_especial > 0:
                tiempo_anuncio_especial -= 1

            contador += 1

            # Enemigos
            for enemigo in enemigos[:]:
                if isinstance(enemigo, EnemigoEspecial):
                    enemigo.mover(nave)
                    enemigo.actualizar_disparos()
                    
                    # Colisión con balas del jugador
                    for bala in balas[:]:
                        if colision(bala.rect, enemigo.rect) and enemigo.tiempo_invulnerable <= 0:
                            enemigo.vida -= 1
                            enemigo.tiempo_invulnerable = 10  # Pequeña invulnerabilidad para evitar daño continuo
                            if bala in balas:
                                balas.remove(bala)
                            if enemigo.vida <= 0:
                                enemigos.remove(enemigo)
                                nave.agregar_puntos(enemigo.puntos)
                                if sonido_explosion:
                                    sonido_explosion.play()
                                explosiones.append(Explosion(enemigo.rect.centerx, enemigo.rect.centery, 
                                                           size_scale=1.5, particle_count=80))
                                
                                # Mayor probabilidad de powerup (50%)
                                if random.random() < 0.5:
                                    tipo = random.choice(["doble_disparo", "escudo", "vida"])
                                    powerups.append(PowerUp(enemigo.rect.centerx, enemigo.rect.centery, tipo))
                            break
                    
                    # Colisión con la nave
                    if colision(nave.rect, enemigo.rect) and nave.invulnerable <= 0 and enemigo.tiempo_invulnerable <= 0 and not god_mode:
                        if enemigo.tipo == "kamikaze":
                            nave.recibir_dano()
                            nave.recibir_dano()  # Doble daño
                            enemigos.remove(enemigo)
                            explosiones.append(Explosion(enemigo.rect.centerx, enemigo.rect.centery, 
                                                       size_scale=1.8, particle_count=100))
                        else:
                            nave.recibir_dano()
                            enemigo.vida -= 1
                            enemigo.tiempo_invulnerable = 20
                            if enemigo.vida <= 0:
                                enemigos.remove(enemigo)
                                nave.agregar_puntos(enemigo.puntos)
                                explosiones.append(Explosion(enemigo.rect.centerx, enemigo.rect.centery, 
                                                           size_scale=1.5, particle_count=80))
                    
                    # Colisión con disparos enemigos
                    if enemigo.disparos:
                        for disparo in enemigo.disparos[:]:
                            if colision(disparo.rect, nave.rect) and nave.invulnerable <= 0 and not god_mode:
                                nave.recibir_dano()
                                enemigo.disparos.remove(disparo)
                                if sonido_explosion:
                                    sonido_explosion.play()
                else:
                    # Comportamiento de enemigos normales
                    enemigo.mover()
                    if colision(nave.rect, enemigo.rect) and nave.invulnerable <= 0 and not god_mode:
                        enemigos.remove(enemigo)
                        nave.recibir_dano()
                        if sonido_explosion:
                            sonido_explosion.play()
                        explosiones.append(Explosion(enemigo.rect.centerx, enemigo.rect.centery))
                        
                        for _ in range(15):
                            particulas_impacto.append(Particula(
                                random.randint(nave.rect.left, nave.rect.right),
                                random.randint(nave.rect.top, nave.rect.bottom),
                                (255, 100, 0),
                                size=random.randint(2, 4),
                                speed=random.uniform(1, 3),
                                angle=random.uniform(0, math.pi * 2),
                                life=random.randint(20, 40)))
                    elif enemigo.rect.top > ALTO:
                        enemigos.remove(enemigo)

            # Balas
            for bala in balas[:]:
                bala.mover()
                if bala.rect.bottom < 0:
                    balas.remove(bala)
                else:
                    for enemigo in enemigos[:]:
                        if colision(bala.rect, enemigo.rect):
                            if isinstance(enemigo, EnemigoEspecial):
                                if enemigo.tiempo_invulnerable <= 0:
                                    enemigo.vida -= 1
                                    enemigo.tiempo_invulnerable = 10
                                    if bala in balas:
                                        balas.remove(bala)
                                    if enemigo.vida <= 0:
                                        enemigos.remove(enemigo)
                                        nave.agregar_puntos(enemigo.puntos)
                                        if sonido_explosion:
                                            sonido_explosion.play()
                                        explosiones.append(Explosion(enemigo.rect.centerx, enemigo.rect.centery, 
                                                                   size_scale=1.5, particle_count=80))
                                        
                                        # Mayor probabilidad de powerup (50%)
                                        if random.random() < 0.5:
                                            tipo = random.choice(["doble_disparo", "escudo", "vida"])
                                            powerups.append(PowerUp(enemigo.rect.centerx, enemigo.rect.centery, tipo))
                            else:
                                enemigos.remove(enemigo)
                                if bala in balas:
                                    balas.remove(bala)
                                nave.agregar_puntos(1)
                                if sonido_explosion:
                                    sonido_explosion.play()
                                explosiones.append(Explosion(enemigo.rect.centerx, enemigo.rect.centery, 0.7, 30))

                                # Probabilidad de soltar powerup
                                if random.random() < 0.15:
                                    tipo = random.choice(["doble_disparo", "escudo", "vida"])
                                    powerups.append(PowerUp(enemigo.rect.centerx, enemigo.rect.centery, tipo))
                            break

            # PowerUps
            for p in powerups[:]:
                p.mover()
                if p.rect.top > ALTO:
                    powerups.remove(p)
                elif colision(p.rect, nave.rect):
                    nave.aplicar_powerup(p.tipo)
                    powerups.remove(p)

        # Actualizaciones visuales (explosiones y partículas)
        explosiones = [e for e in explosiones if e.update()]
        particulas_impacto = [p for p in particulas_impacto if p.update()]
        particulas_impulso = [p for p in particulas_impulso if p.update()]

        for explosion in explosiones:
            explosion.draw(PANTALLA)
        
        for particula in particulas_impacto:
            particula.draw(PANTALLA)
        
        for particula in particulas_impulso:
            particula.draw(PANTALLA)
        
        # Dibujo entidades
        for enemigo in enemigos:
            if isinstance(enemigo, EnemigoEspecial):
                enemigo.dibujar()
                enemigo.dibujar_disparos()
            else:
                enemigo.dibujar()
        
        for bala in balas:
            bala.dibujar()
        
        for p in powerups:
            p.dibujar()

        nave.dibujar()

        # HUD
        mostrar_texto_sombra("VIDAS: " + str(nave.vida), 20, 10, (255, 50, 50), (0, 0, 0))
        mostrar_texto_sombra("PUNTAJE: " + str(nave.puntaje), 20, 40, (255, 255, 255), (0, 0, 0))
        
        # Barra de vida
        pygame.draw.rect(PANTALLA, (50, 50, 50), (120, 15, 100, 20))
        pygame.draw.rect(PANTALLA, (255, 50, 50), (120, 15, 100 * (nave.vida / nave.vida_maxima), 20))

        # Indicadores de power-ups
        hud_y = 70
        if nave.doble_disparo_ticks > 0:
            segundos = math.ceil(nave.doble_disparo_ticks / 60)
            mostrar_texto_sombra(f"Doble disparo: {segundos}s", 20, hud_y, (0, 255, 0), (0, 0, 0), 22, False)
            hud_y += 24
        if nave.escudo_ticks > 0:
            segundos = math.ceil(nave.escudo_ticks / 60)
            mostrar_texto_sombra(f"Escudo: {segundos}s", 20, hud_y, (0, 180, 255), (0, 0, 0), 22, False)
            hud_y += 24
        
        # Indicador de próximo enemigo especial
        puntos_faltantes = max(0, siguiente_enemigo_especial - nave.puntaje)
        mostrar_texto_sombra(f"Próximo especial: {puntos_faltantes}", ANCHO - 200, 40, (255, 255, 0), (0, 0, 0), 18, False)
        
        # Mostrar mensaje de enemigo especial si está activo
        if tiempo_anuncio_especial > 0:
            alpha = min(255, tiempo_anuncio_especial * 2)
            texto_surf = fuente.render(mensaje_especial, True, (255, 255, 255))
            overlay = pygame.Surface((texto_surf.get_width() + 20, texto_surf.get_height() + 10), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, alpha // 2))
            pygame.draw.rect(overlay, (255, 215, 0, alpha), overlay.get_rect(), 2, border_radius=5)
            PANTALLA.blit(overlay, (ANCHO//2 - overlay.get_width()//2, 50))
            texto_surf.set_alpha(alpha)
            PANTALLA.blit(texto_surf, (ANCHO//2 - texto_surf.get_width()//2, 55))
        
        mostrar_texto_sombra("P para pausar", ANCHO - 150, 10, (200, 200, 200), (0, 0, 0), 18, False)
        
        # Mostrar modo dios si está activo
        if god_mode:
            mostrar_texto_sombra("MODO DIOS ACTIVADO", ANCHO//2, 80, (255, 0, 0), (0, 0, 0), 24, True)

        if nave.vida <= 0 and not god_mode:
            game_over = True
            nave.puntaje_total += nave.puntaje
            if nave.puntaje > nave.puntaje_maximo:
                nave.puntaje_maximo = nave.puntaje
            nave.guardar_progreso()
            
            resultado = mostrar_game_over(nave)
            if resultado == "restart":
                return "restart"
            elif resultado == "menu":
                return "menu"

        # Dibujar consola si está visible
        consola.dibujar(PANTALLA)

        pygame.display.update()

def main_loop():
    mostrar_pantalla_carga("Inicializando juego...")
    
    while True:
        menu()
        resultado = main()
        if resultado == "menu":
            continue
        elif resultado == "restart":
            mostrar_pantalla_carga("Preparando nueva partida...")

if __name__ == "__main__":
    main_loop()