from django.db import models
from django.contrib.auth.models import User
from computations.models import Computation
class ComputationResult(models.Model):
    computation=models.OneToOneField(Computation,on_delete=models.CASCADE,related_name='result')
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='results')
    total_energy=models.FloatField(null=True)
    hartree_fock_energy=models.FloatField(null=True)
    kinetic_energy=models.FloatField(null=True)
    potential_energy=models.FloatField(null=True)
    exchange_energy=models.FloatField(null=True)
    correlation_energy=models.FloatField(null=True)
    homo_energy=models.FloatField(null=True)
    lumo_energy=models.FloatField(null=True)
    orbital_data=models.JSONField(default=dict)
    density_matrix=models.JSONField(default=dict)
    charge_distribution=models.JSONField(default=dict)
    dipole_moment=models.FloatField(null=True)
    quadrupole_moment=models.FloatField(null=True)
    polarizability=models.FloatField(null=True)
    result_file=models.FileField(upload_to='results/%Y/%m/%d/',null=True,blank=True)
    output_log=models.TextField(blank=True)
    convergence_info=models.JSONField(default=dict)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table='computation_results'
        indexes=[models.Index(fields=['user','-created_at']),]
class ResultVisualization(models.Model):
    result=models.ForeignKey(ComputationResult,on_delete=models.CASCADE,related_name='visualizations')
    title=models.CharField(max_length=255)
    plot_type=models.CharField(max_length=50,choices=[('orbital','Orbital'),('density','Density'),('potential','Potential'),('spectrum','Spectrum')])
    plot_data=models.JSONField()
    plot_image=models.ImageField(upload_to='visualizations/%Y/%m/%d/',null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table='result_visualizations'
class Export(models.Model):
    FORMAT_CHOICES=[('csv','CSV'),('json','JSON'),('hdf5','HDF5'),('molden','MOLDEN'),('xyz','XYZ'),]
    result=models.ForeignKey(ComputationResult,on_delete=models.CASCADE,related_name='exports')
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    format=models.CharField(max_length=50,choices=FORMAT_CHOICES)
    file=models.FileField(upload_to='exports/%Y/%m/%d/')
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table='exports'
