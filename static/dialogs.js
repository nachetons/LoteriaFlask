function showAlert(sorteo,fecha,numero,extra){
    const swalWithBootstrapButtons = Swal.mixin({
      customClass: {
        confirmButton: 'btn btn-success',
        cancelButton: 'btn btn-danger'
      },
      buttonsStyling: false
    })
    
    swalWithBootstrapButtons.fire({
      title: 'Are you sure?',
      text: "You won't be able to revert this!",
      icon: 'warning',
      showCancelButton: true,
      confirmButtonText: 'Yes, delete it!',
      cancelButtonText: 'No, cancel!',
      reverseButtons: true
    }).then((result) => {
      if (result.isConfirmed) {
        swalWithBootstrapButtons.fire(
          'Deleted!',
          'Your file has been deleted.',
          'success'
        )
        const form = document.getElementById('my-form');
        form.action = '/marcadores'; // actualizar la acción del formulario
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'data';
        input.value = sorteo + ',' + fecha + ',' + numero + ',' + extra;
        form.appendChild(input); // agregar el campo de datos al formulario
        form.submit();

      } else if (
        /* Read more about handling dismissals below */
        result.dismiss === Swal.DismissReason.cancel
      ) {
        swalWithBootstrapButtons.fire(
          'Cancelled',
          'Your imaginary file is safe :)',
          'error'
        )
      }
    })

  }

    function showDeleteSucess(){
        Swal.fire(
            'Borrado!',
            'Tu boleto fue eliminado.',
            'success'
          )
    }

    function showDeleteError(){
        Swal.fire(
            'Error!',
            'Tu boleto no pudo ser eliminado.',
            'error'
          )
    }

    