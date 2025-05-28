import pygame
import matplotlib.pyplot as plt
import numpy as np
import io

# Step 1: Create matplotlib figure
fig, axs = plt.subplots(1, 2, figsize=(4, 2))  # 1 row, 2 columns

x = np.linspace(0, 10, 100)
axs[0].plot(x, np.sin(x))
axs[0].set_title('Sine')

axs[1].plot(x, np.cos(x))
axs[1].set_title('Cosine')

plt.tight_layout()

# Step 2: Save plot to a bytes buffer
buf = io.BytesIO()
plt.savefig(buf, format='PNG')
buf.seek(0)
plt.close()

# Step 3: Load the image into Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Pygame with Subplot")

plot_image = pygame.image.load(buf).convert()
plot_rect = plot_image.get_rect(center=(400, 300))

# Main loop
running = True
while running:
    screen.fill((255, 255, 255))  # White background
    screen.blit(plot_image, plot_rect)  # Draw subplot image

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()

pygame.quit()