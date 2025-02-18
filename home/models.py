from django.db import models

class Versao(models.Model):
    
    TIPO_CHOICES = (
        ('bug', 'Bug'),
        ('funcionalidade', 'Funcionalidade'),
        ('implementacao', 'Implementação'),
    )
    
    numero = models.CharField(max_length=10, unique=True, blank=True)
    data_lancamento = models.DateField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    descricao = models.TextField()

    def save(self, *args, **kwargs):
        if not self.pk:  # Só gera uma nova versão se for um novo registro
            ultima_versao = Versao.objects.order_by('-data_lancamento').first()

            if ultima_versao:
                partes = [int(x) for x in ultima_versao.numero.split('.')]  # Divide a versão em [X, Y, Z]
            else:
                partes = [0, 0, 0]  # Se não houver versões, inicia com "1.0.0"

            # Define o incremento com base no tipo de alteração
            if self.tipo == 'bug':
                partes[2] += 1  # Ex: 1.0.1 → 1.0.2
            elif self.tipo == 'funcionalidade':
                partes[1] += 1  # Ex: 1.1.0 → 1.2.0
                partes[2] = 0  # Reinicia o último número
            elif self.tipo == 'implementacao':
                partes[0] += 1  # Ex: 2.0.0 → 3.0.0
                partes[1] = 0
                partes[2] = 0  # Reinicia os números menores

            self.numero = f"{partes[0]}.{partes[1]}.{partes[2]}"  # Monta a nova versão

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Versão {self.numero}"