#include <Python.h>
#include "structmember.h"


typedef struct
{
  PyObject_HEAD
  PyObject * data;
} Node;


static void
Node_dealloc (Node * self)
{
  Py_XDECREF (self->data);
  self->ob_type->tp_free ((PyObject *) self);
}


static PyObject *
Node_new (PyTypeObject * type, PyObject * args, PyObject * kwds)
{
  Node *self;

  self = (Node *) type->tp_alloc (type, 0);
  if (self != NULL)
    {
      /* We store None, by default */
      Py_INCREF (Py_None);
      self->data = Py_None;
    }

  return (PyObject *) self;
}


static int
Node_init (Node * self, PyObject * args, PyObject * kwds)
{
  PyObject *data = NULL, *tmp;
  static char *kwlist[] = { "data", NULL };

  if (!PyArg_ParseTupleAndKeywords (args, kwds, "|O", kwlist, &data))
    return -1;

  if (data)
    {
      tmp = self->data;
      Py_INCREF (data);
      self->data = data;
      Py_XDECREF (tmp);
    }

  return 0;
}


static PyMethodDef Node_methods[] = {
  {NULL}                        /* Sentinel */
};


static PyMemberDef Node_members[] = {
  {"data", T_OBJECT_EX, offsetof (Node, data), 0, "data"},
  {NULL}                        /* Sentinel */
};


static PyTypeObject NodeType = {
  PyObject_HEAD_INIT (NULL) 0,  /*ob_size */
  "gss.Node",                   /*tp_name */
  sizeof (Node),                /*tp_basicsize */
  0,                            /*tp_itemsize */
  (destructor) Node_dealloc,    /*tp_dealloc */
  0,                            /*tp_print */
  0,                            /*tp_getattr */
  0,                            /*tp_setattr */
  0,                            /*tp_compare */
  0,                            /*tp_repr */
  0,                            /*tp_as_number */
  0,                            /*tp_as_sequence */
  0,                            /*tp_as_mapping */
  0,                            /*tp_hash */
  0,                            /*tp_call */
  0,                            /*tp_str */
  0,                            /*tp_getattro */
  0,                            /*tp_setattro */
  0,                            /*tp_as_buffer */
  Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,     /*tp_flags */
  "Node object",                /* tp_doc */
  0,                            /* tp_traverse */
  0,                            /* tp_clear */
  0,                            /* tp_richcompare */
  0,                            /* tp_weaklistoffset */
  0,                            /* tp_iter */
  0,                            /* tp_iternext */
  Node_methods,                 /* tp_methods */
  Node_members,                 /* tp_members */
  0,                            /* tp_getset */
  0,                            /* tp_base */
  0,                            /* tp_dict */
  0,                            /* tp_descr_get */
  0,                            /* tp_descr_set */
  0,                            /* tp_dictoffset */
  (initproc) Node_init,         /* tp_init */
  0,                            /* tp_alloc */
  Node_new,                     /* tp_new */
};

static PyMethodDef module_methods[] = {
  {NULL}                        /* Sentinel */
};

#ifndef PyMODINIT_FUNC          /* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
initgss (void)
{
  PyObject *m;

  if (PyType_Ready (&NodeType) < 0)
    return;

  m = Py_InitModule3 ("gss", module_methods,
                      "A fast implementation of a GSS.");

  if (m == NULL)
    return;

  Py_INCREF (&NodeType);
  PyModule_AddObject (m, "Node", (PyObject *) & NodeType);
}
