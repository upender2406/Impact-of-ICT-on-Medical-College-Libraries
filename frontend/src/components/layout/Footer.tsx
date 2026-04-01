export function Footer() {
  return (
    <footer className="border-t border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-900">
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
          <div>
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white">
              ICT Impact Assessment Dashboard
            </h3>
            <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
              AI-powered analysis platform for medical college libraries in Bihar
            </p>
          </div>
          <div>
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white">Resources</h3>
            <ul className="mt-2 space-y-2 text-sm text-gray-600 dark:text-gray-400">
              <li>
                <a href="#" className="hover:text-primary-600">
                  Documentation
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-primary-600">
                  API Reference
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-primary-600">
                  Support
                </a>
              </li>
            </ul>
          </div>
          <div>
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white">Contact</h3>
            <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
              For inquiries and support, please contact the research team.
            </p>
          </div>
        </div>
        <div className="mt-8 border-t border-gray-200 pt-8 dark:border-gray-800">
          <p className="text-center text-sm text-gray-600 dark:text-gray-400">
            © {new Date().getFullYear()} ICT Impact Assessment Dashboard. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}
