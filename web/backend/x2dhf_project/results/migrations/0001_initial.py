from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('computations', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ComputationResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_energy', models.FloatField(null=True)),
                ('hartree_fock_energy', models.FloatField(null=True)),
                ('kinetic_energy', models.FloatField(null=True)),
                ('potential_energy', models.FloatField(null=True)),
                ('exchange_energy', models.FloatField(null=True)),
                ('correlation_energy', models.FloatField(null=True)),
                ('homo_energy', models.FloatField(null=True)),
                ('lumo_energy', models.FloatField(null=True)),
                ('orbital_data', models.JSONField(default=dict)),
                ('density_matrix', models.JSONField(default=dict)),
                ('charge_distribution', models.JSONField(default=dict)),
                ('dipole_moment', models.FloatField(null=True)),
                ('quadrupole_moment', models.FloatField(null=True)),
                ('polarizability', models.FloatField(null=True)),
                ('result_file', models.FileField(blank=True, null=True, upload_to='results/%Y/%m/%d/')),
                ('output_log', models.TextField(blank=True)),
                ('convergence_info', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('computation', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='result', to='computations.computation')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'computation_results',
            },
        ),
        migrations.CreateModel(
            name='ResultVisualization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('plot_type', models.CharField(choices=[('orbital', 'Orbital'), ('density', 'Density'), ('potential', 'Potential'), ('spectrum', 'Spectrum')], max_length=50)),
                ('plot_data', models.JSONField()),
                ('plot_image', models.ImageField(blank=True, null=True, upload_to='visualizations/%Y/%m/%d/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('result', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='visualizations', to='results.computationresult')),
            ],
            options={
                'db_table': 'result_visualizations',
            },
        ),
        migrations.CreateModel(
            name='Export',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('format', models.CharField(choices=[('csv', 'CSV'), ('json', 'JSON'), ('hdf5', 'HDF5'), ('molden', 'MOLDEN'), ('xyz', 'XYZ')], max_length=50)),
                ('file', models.FileField(upload_to='exports/%Y/%m/%d/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('result', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exports', to='results.computationresult')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'exports',
            },
        ),
        migrations.AddIndex(
            model_name='computationresult',
            index=models.Index(fields=['user', '-created_at'], name='computation_user_id_ae8a37_idx'),
        ),
    ]
